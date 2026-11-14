"""Check planning documents and synthetic examples; this is not the app engine.

AI-assisted authoring is recorded in docs/AI_USAGE.md. Uses only Python stdlib.
"""

import json
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {
    ".git", ".venv", "node_modules", "dist", "coverage", "__pycache__",
    "raw", "intermediate", "processed", "cache", "playwright-report",
}
TASK_ID = re.compile(r"[KEI]-\d{3}")
STATES = {"todo", "in_progress", "blocked", "review", "done", "cancelled"}


def project_files():
    for directory, subdirs, files in os.walk(ROOT):
        subdirs[:] = [name for name in subdirs if name not in EXCLUDED]
        for name in files:
            yield Path(directory) / name


def reference_scores(case):
    """Independent arithmetic check of the documented, equal-area test vectors."""
    weights = case["weights"]
    assert weights and all(math.isfinite(w) and w > 0 for w in weights.values())
    denominator = sum(weights.values())
    ranked, excluded = [], []
    groups = defaultdict(list)
    for pixel in case["pixels"]:
        group = pixel["map_cell_id"]
        groups[group]  # Keep empty map buckets for missing-only cases.
        if any(pixel["values"].get(feature) is None for feature in weights):
            excluded.append(pixel["pixel_id"])
            continue
        score = 0.0
        for feature, weight in weights.items():
            definition = case["features"][feature]
            low, high = definition["interval"]
            tolerance = definition["tolerance"]
            assert low <= high and tolerance > 0
            value = pixel["values"][feature]
            distance = max(low - value, 0, value - high)
            similarity = max(0, 1 - distance / tolerance)
            score += 100 * weight / denominator * similarity
        ranked.append((pixel["pixel_id"], score))
        groups[group].append((pixel["pixel_id"], score))
    ranked.sort(key=lambda item: (-item[1], item[0]))
    aggregates = {}
    for name, values in groups.items():
        values.sort(key=lambda item: (-item[1], item[0]))
        aggregates[name] = {
            "max_score_pct": values[0][1] if values else None,
            "mean_score_pct": sum(score for _, score in values) / len(values) if values else None,
            "max_pixel_id": values[0][0] if values else None,
        }
    return ranked, sorted(excluded), aggregates


def equal_value(actual, expected):
    if isinstance(expected, (int, float)):
        return actual is not None and math.isclose(actual, expected, abs_tol=1e-8)
    return actual == expected


def main():
    errors = []
    files = list(project_files())
    markdown = [path for path in files if path.suffix == ".md"]
    json_files = [path for path in files if path.suffix == ".json"]
    texts = {path: path.read_text(encoding="utf-8") for path in markdown}

    for path, content in texts.items():
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^\n)]+)\)", content):
            target = target.strip().strip("<>")
            if target.startswith("#") or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            target = unquote(target.split("#", 1)[0])
            if target and not (path.parent / target).resolve().exists():
                errors.append(f"Broken link in {path.relative_to(ROOT)}: {target}")

    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")

    cards = {}
    for path in sorted((ROOT / "tasks").glob("*.md")):
        if not TASK_ID.fullmatch(path.stem):
            continue
        content = texts[path]
        match = re.match(r"---\n(.*?)\n---\n", content, re.DOTALL)
        if not match:
            errors.append(f"Missing task metadata: {path.name}")
            continue
        metadata = {}
        for line in match.group(1).splitlines():
            key, separator, value = line.partition(":")
            if not separator or key in metadata:
                errors.append(f"Invalid or duplicate task metadata: {path.name}: {line}")
                continue
            metadata[key] = value.strip()
        required = {
            "id", "owner", "reviewer", "priority", "status", "depends_on",
            "agent", "work_branch", "updated", "discovered_from",
        }
        if required - metadata.keys():
            errors.append(f"Missing fields in {path.name}: {required - metadata.keys()}")
        if metadata.get("id") != path.stem:
            errors.append(f"ID does not match filename: {path.name}")
        if metadata.get("owner") not in {"kamil", "ewelina"}:
            errors.append(f"Unknown owner: {path.name}")
        if metadata.get("reviewer") not in {"kamil", "ewelina"} or metadata.get("reviewer") == metadata.get("owner"):
            errors.append(f"Invalid reviewer: {path.name}")
        if metadata.get("priority") not in {"P0", "P1", "P2"} or metadata.get("status") not in STATES:
            errors.append(f"Invalid priority/status: {path.name}")
        if metadata.get("status") in {"in_progress", "review", "done"}:
            if metadata.get("agent") in {None, "", "unassigned"} or metadata.get("work_branch") in {None, "", "unassigned"}:
                errors.append(f"Started task needs an agent and work branch: {path.name}")
        raw_dependencies = metadata.get("depends_on", "")
        if not (raw_dependencies.startswith("[") and raw_dependencies.endswith("]")):
            errors.append(f"Dependencies must use a one-line list: {path.name}")
        metadata["dependencies"] = [item.strip() for item in raw_dependencies.strip("[]").split(",") if item.strip()]
        if len(metadata["dependencies"]) != len(set(metadata["dependencies"])):
            errors.append(f"Duplicate dependencies: {path.name}")
        if metadata.get("status") == "done":
            acceptance = content.split("## Kryteria odbioru", 1)[-1].split("## Sprawdzenie", 1)[0]
            if "- [ ]" in acceptance:
                errors.append(f"Done task has unchecked acceptance criteria: {path.name}")
        if f"]({path.name})" not in texts[ROOT / "tasks" / "README.md"]:
            errors.append(f"Task missing from index: {path.name}")
        cards[path.stem] = metadata

    for task_id, metadata in cards.items():
        for dependency in metadata["dependencies"]:
            if dependency not in cards:
                errors.append(f"Unknown dependency {dependency} in {task_id}")
    visited, active = set(), set()

    def visit(task_id):
        if task_id in active:
            errors.append(f"Dependency cycle at {task_id}")
            return
        if task_id in visited or task_id not in cards:
            return
        active.add(task_id)
        for dependency in cards[task_id]["dependencies"]:
            visit(dependency)
        active.remove(task_id)
        visited.add(task_id)

    for task_id in cards:
        visit(task_id)

    checked_cases = 0
    fixture_path = ROOT / "contracts" / "fixtures" / "hotspot-regression.json"
    try:
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        assert fixture["is_synthetic"] is True and fixture["ai_assisted"] is True
        for case in fixture["cases"]:
            ranked, excluded, groups = reference_scores(case)
            expected = case["expected"]
            assert [pixel_id for pixel_id, _ in ranked] == expected["ranked_pixel_ids"], case["id"]
            assert excluded == sorted(expected.get("excluded_pixel_ids", [])), case["id"]
            assert equal_value(ranked[0][1] if ranked else None, expected["top_score_pct"]), case["id"]
            assert groups.keys() == expected["map_cells"].keys(), case["id"]
            for group, fields in expected["map_cells"].items():
                for key, value in fields.items():
                    assert equal_value(groups[group][key], value), (case["id"], group, key)
            checked_cases += 1
    except (AssertionError, KeyError, ValueError, TypeError, ZeroDivisionError) as exc:
        errors.append(f"Synthetic fixture check failed: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(markdown)} Markdown files, {len(json_files)} JSON files, {len(cards)} task cards, acyclic dependencies, {checked_cases} synthetic cases.")
    print("Checks cover planning documents and example arithmetic, not an implemented application or real scientific data.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
