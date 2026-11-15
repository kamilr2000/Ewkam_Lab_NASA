"""Download and verify the public ETOPO and GSHHG inputs pinned by K-042."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from pipeline.download_k017_assets import download_public_file, extract_gshhg_archive
from pipeline.global_grid_pilot import ETOPO_RECORDS, GSHHG_RECORD


REPO_ROOT = Path(__file__).resolve().parents[1]


def ensure_sources(*, verify_only: bool = False) -> list[dict[str, object]]:
    """Fetch or verify each unique public input, then extract GSHHG polygons."""
    records_by_name = {str(record["filename"]): record for record in ETOPO_RECORDS.values()}
    records_by_name[str(GSHHG_RECORD["filename"])] = GSHHG_RECORD
    verified: list[dict[str, object]] = []

    for filename in sorted(records_by_name):
        record = records_by_name[filename]
        destination = REPO_ROOT / str(record["path"])
        if verify_only and not destination.is_file():
            raise FileNotFoundError(f"Missing pinned source: {record['path']}")
        size, digest = download_public_file(record, destination.parent)
        verified.append(
            {
                "filename": filename,
                "path": str(record["path"]),
                "size_bytes": size,
                "sha256": digest,
            }
        )

    archive = REPO_ROOT / str(GSHHG_RECORD["path"])
    extract_dir = archive.parent / "extracted"
    extract_gshhg_archive(archive, extract_dir)
    return verified


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Check existing pinned files without downloading missing sources.",
    )
    args = parser.parse_args()
    try:
        for record in ensure_sources(verify_only=args.verify_only):
            print(
                f"verified {record['filename']}: {record['size_bytes']} bytes "
                f"sha256={record['sha256']}"
            )
    except (OSError, TypeError, ValueError, RuntimeError) as error:
        print(f"K-042 source preparation failed: {error}", file=sys.stderr)
        return 1

    print("K-042 public sources verified; no Earthdata token is required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
