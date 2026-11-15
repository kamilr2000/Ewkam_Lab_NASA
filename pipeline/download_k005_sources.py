"""Download only the public ETOPO/GSHHG inputs required by K-005."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from download_k017_assets import download_public_file, extract_gshhg_archive


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "manifests" / "k017-earth-validation.json"
RAW_ROOT = REPO_ROOT / "data" / "raw" / "k017"


def _file_record(manifest: dict[str, object], filename: str) -> dict[str, object]:
    for dataset in manifest["datasets"]:
        for record in dataset.get("files", []):
            if record.get("filename") == filename:
                return record
    raise KeyError(f"No pinned source record for {filename}")


def download() -> list[dict[str, object]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    filenames = sorted({Path(aoi["etopo_file"]).name for aoi in manifest["comparison_aois"]})
    etopo_dir = RAW_ROOT / "etopo"
    gshhg_dir = RAW_ROOT / "gshhg"
    etopo_dir.mkdir(parents=True, exist_ok=True)
    gshhg_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for filename in filenames:
        record = _file_record(manifest, filename)
        size_bytes, digest = download_public_file(record, etopo_dir)
        item = {"filename": filename, "size_bytes": size_bytes, "sha256": digest}
        records.append(item)
        print(f"verified public ETOPO {filename}: {size_bytes} bytes sha256={digest}")

    gshhg_record = _file_record(manifest, "gshhg-shp-2.3.7.zip")
    gshhg_path = gshhg_dir / "gshhg-shp-2.3.7.zip"
    size_bytes, digest = download_public_file(gshhg_record, gshhg_dir)
    extract_gshhg_archive(gshhg_path, gshhg_dir / "extracted")
    records.append({"filename": gshhg_path.name, "size_bytes": size_bytes, "sha256": digest})
    print(f"verified public GSHHG {gshhg_path.name}: {size_bytes} bytes sha256={digest}")
    print("K-005 public source assets are ready; no Earthdata token is required.")
    return records


def main() -> int:
    try:
        download()
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(f"K-005 source download failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
