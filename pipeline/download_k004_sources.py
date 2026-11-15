"""Download and verify the public K-004 planetary-profile source files."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "manifests" / "k004-source-files.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "raw" / "k004"


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
    url = str(record["url"])
    if urlparse(url).scheme != "https":
        raise ValueError(f"Refusing non-HTTPS source for {filename}")

    destination = output_dir / filename
    if destination.exists():
        verify_file(destination, record)
        return f"verified existing {filename}"

    temporary = destination.with_name(destination.name + ".part")
    request = Request(url, headers={"User-Agent": "terra-analog-k004-source-fetch/1.0"})
    try:
        with urlopen(request, timeout=180) as response, temporary.open("wb") as target:
            shutil.copyfileobj(response, target, length=1024 * 1024)
        verify_file(temporary, record)
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return f"downloaded and verified {filename}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download and verify the pinned public K-004 data and source labels."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Pinned source file manifest.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Output directory for raw inputs.")
    args = parser.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if manifest.get("manifest_version") != 1 or manifest.get("task_id") != "K-004":
            raise ValueError("Unsupported K-004 input manifest.")
        records = manifest.get("files")
        if not isinstance(records, list) or not records:
            raise ValueError("K-004 input manifest contains no files.")
        filenames = [record.get("filename") for record in records if isinstance(record, dict)]
        if len(filenames) != len(records) or len(set(filenames)) != len(filenames):
            raise ValueError("K-004 input manifest has invalid or duplicate file records.")

        args.output_dir.mkdir(parents=True, exist_ok=True)
        for record in records:
            print(download_one(record, args.output_dir), flush=True)
        print(f"Verified {len(records)} files from {args.manifest}")
    except (KeyError, OSError, TypeError, ValueError, URLError) as error:
        print(f"K-004 source download failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
