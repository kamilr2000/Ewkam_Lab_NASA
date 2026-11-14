"""Download the small public sample files listed in data/manifests/k002-samples.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "manifests" / "k002-samples.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "raw" / "k002"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, record: dict[str, object]) -> None:
    expected_size = int(record["size_bytes"])
    expected_hash = str(record["sha256"]).lower()
    if path.stat().st_size != expected_size:
        raise ValueError(
            f"{path.name}: size mismatch; expected {expected_size} bytes, "
            f"got {path.stat().st_size}"
        )
    actual_hash = sha256_file(path)
    if actual_hash != expected_hash:
        raise ValueError(
            f"{path.name}: SHA-256 mismatch; expected {expected_hash}, got {actual_hash}"
        )


def download_one(record: dict[str, object], output_dir: Path) -> str:
    filename = str(record["filename"])
    if not filename or Path(filename).name != filename or "/" in filename or "\\" in filename:
        raise ValueError(f"Unsafe manifest filename: {filename!r}")

    destination = output_dir / filename
    if destination.exists():
        verify_file(destination, record)
        return f"verified existing {filename}"

    temporary = destination.with_name(destination.name + ".part")
    request = Request(
        str(record["url"]),
        headers={"User-Agent": "terra-analog-k002-sample-fetch/1.0"},
    )
    try:
        with urlopen(request, timeout=90) as response, temporary.open("wb") as target:
            shutil.copyfileobj(response, target, length=1024 * 1024)
        verify_file(temporary, record)
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return f"downloaded and verified {filename}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download and verify the public K-002 source-audit samples."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Sample manifest (default: data/manifests/k002-samples.json).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory (default: data/raw/k002).",
    )
    args = parser.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        records = [
            file_record
            for dataset in manifest["datasets"]
            for file_record in dataset.get("files", [])
        ]
        if not records:
            raise ValueError("Manifest contains no downloadable sample files.")

        args.output_dir.mkdir(parents=True, exist_ok=True)
        for record in records:
            print(download_one(record, args.output_dir))
        print(f"Verified {len(records)} files from {args.manifest}")
    except (KeyError, OSError, TypeError, ValueError, URLError) as error:
        print(f"Sample download failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
