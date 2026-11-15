"""Fetch and verify K-017 NASADEM and public validation assets.

Raw archives and extracted products stay under the ignored data/raw/k017 tree.
The script never reads, prints, or writes an Earthdata token; earthaccess reads
EARTHDATA_TOKEN from the process environment when an authenticated tile is needed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.error import URLError
from urllib.request import Request, urlopen

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "manifests" / "k017-earth-validation.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "raw" / "k017"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_pinned(path: Path, record: dict[str, object]) -> tuple[int, str]:
    actual_size = path.stat().st_size
    actual_hash = sha256_file(path)
    expected_size = record.get("size_bytes")
    expected_hash = record.get("sha256")
    if expected_size is not None and actual_size != int(expected_size):
        raise ValueError(
            f"{path.name}: expected {expected_size} bytes, received {actual_size}"
        )
    if expected_hash is not None and actual_hash != str(expected_hash).lower():
        raise ValueError(
            f"{path.name}: SHA-256 mismatch; expected {expected_hash}, got {actual_hash}"
        )
    return actual_size, actual_hash


def safe_filename(value: object) -> str:
    filename = str(value)
    if not filename or Path(filename).name != filename or "/" in filename or "\\" in filename:
        raise ValueError(f"Unsafe manifest filename: {filename!r}")
    return filename


def download_public_file(record: dict[str, object], output_dir: Path) -> tuple[int, str]:
    filename = safe_filename(record["filename"])
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / filename
    if destination.exists():
        return verify_pinned(destination, record)

    temporary = destination.with_name(destination.name + ".part")
    request = Request(
        str(record["url"]),
        headers={"User-Agent": "terra-analog-k017-validation/1.0"},
    )
    try:
        with urlopen(request, timeout=180) as response, temporary.open("wb") as target:
            shutil.copyfileobj(response, target, length=1024 * 1024)
        actual = verify_pinned(temporary, record)
        temporary.replace(destination)
        return actual
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def extract_gshhg_archive(archive: Path, output_dir: Path) -> None:
    sentinel = output_dir / "GSHHS_shp" / "f" / "GSHHS_f_L6.shp"
    if sentinel.is_file():
        return
    with zipfile.ZipFile(archive) as source:
        for info in source.infolist():
            member_parts = safe_archive_parts(info.filename)
            destination = output_dir.joinpath(*member_parts)
            if info.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source.open(info) as input_file, destination.open("wb") as output_file:
                shutil.copyfileobj(input_file, output_file, length=1024 * 1024)
    for level in (1, 2, 3, 4, 5, 6):
        if not (output_dir / "GSHHS_shp" / "f" / f"GSHHS_f_L{level}.shp").is_file():
            raise ValueError(f"GSHHG archive is missing full-resolution L{level} shapefile")


def tile_suffix(granule_id: str) -> str:
    prefix = "NASADEM_HGT_"
    if not granule_id.startswith(prefix):
        raise ValueError(f"Unexpected NASADEM granule id: {granule_id}")
    return granule_id.removeprefix(prefix)


def safe_zip_member(info: zipfile.ZipInfo) -> str:
    return safe_archive_parts(info.filename)[-1]


def safe_archive_parts(filename: str) -> tuple[str, ...]:
    posix = PurePosixPath(filename)
    windows = PureWindowsPath(filename)
    if (
        posix.is_absolute()
        or not posix.parts
        or windows.is_absolute()
        or windows.drive
        or windows.root
        or ".." in posix.parts
        or ".." in windows.parts
    ):
        raise ValueError(f"Unsafe archive path: {filename!r}")
    return posix.parts


def inspect_nasadem_layers(layer_paths: dict[str, Path]) -> dict[str, object]:
    expected_samples = 3601 * 3601
    hgt = np.fromfile(layer_paths["hgt"], dtype=">i2")
    num = np.fromfile(layer_paths["num"], dtype="uint8")
    swb = np.fromfile(layer_paths["swb"], dtype="uint8")
    for layer, values in (("hgt", hgt), ("num", num), ("swb", swb)):
        if values.size != expected_samples:
            raise ValueError(
                f"{layer_paths[layer].name}: expected {expected_samples} samples, got {values.size}"
            )

    hgt_min = int(hgt.min())
    hgt_max = int(hgt.max())
    if hgt_min < -32767 or hgt_max > 32767:
        raise ValueError(
            f"{layer_paths['hgt'].name}: HGT values outside documented range: {hgt_min}..{hgt_max}"
        )
    allowed_num = (
        (num == 0)
        | ((num >= 1) & (num <= 23))
        | ((num >= 41) & (num <= 94))
        | ((num >= 110) & (num <= 160))
        | ((num >= 170) & (num <= 220))
        | ((num >= 231) & (num <= 234))
        | ((num >= 241) & (num <= 246))
        | (num == 250)
        | (num == 251)
        | (num == 255)
    )
    if not bool(np.all(allowed_num)):
        unexpected = sorted(set(map(int, np.unique(num[~allowed_num]))))
        raise ValueError(f"{layer_paths['num'].name}: undocumented NUM classes {unexpected}")
    if not bool(np.all((swb == 0) | (swb == 255))):
        unexpected = sorted(set(map(int, np.unique(swb[(swb != 0) & (swb != 255)]))))
        raise ValueError(f"{layer_paths['swb'].name}: undocumented SWB classes {unexpected}")

    num_values, num_counts = np.unique(num, return_counts=True)
    swb_values, swb_counts = np.unique(swb, return_counts=True)
    return {
        "sample_count_per_layer": expected_samples,
        "hgt_m_egm96": {
            "minimum": hgt_min,
            "maximum": hgt_max,
            "outside_documented_range_count": 0,
        },
        "num_class_histogram": {
            str(int(value)): int(count) for value, count in zip(num_values, num_counts)
        },
        "swb_class_histogram": {
            str(int(value)): int(count) for value, count in zip(swb_values, swb_counts)
        },
    }


def validate_nasadem_products(tile: dict[str, object], raw_dir: Path) -> list[dict[str, object]]:
    granule_id = str(tile["granule_id"])
    suffix = tile_suffix(granule_id)
    archive_name = safe_filename(tile["archive_filename"])
    archive = raw_dir / "nasadem" / archive_name
    if not archive.is_file():
        raise FileNotFoundError(f"Missing NASADEM archive: {archive}")

    archive_size, archive_hash = verify_pinned(
        archive,
        {"size_bytes": tile.get("archive_size_bytes"), "sha256": tile.get("archive_sha256")},
    )
    expected_members = {layer: f"{suffix}.{layer}" for layer in ("hgt", "num", "swb")}
    with zipfile.ZipFile(archive) as source:
        member_by_layer: dict[str, zipfile.ZipInfo] = {}
        for info in source.infolist():
            if info.is_dir():
                continue
            member_name = safe_zip_member(info)
            for layer, expected_name in expected_members.items():
                if member_name.lower() == expected_name.lower():
                    if layer in member_by_layer:
                        raise ValueError(f"Duplicate {layer} member in {archive_name}")
                    member_by_layer[layer] = info
        if set(member_by_layer) != set(expected_members):
            missing = sorted(set(expected_members) - set(member_by_layer))
            raise ValueError(f"{archive_name}: missing NASADEM layers: {', '.join(missing)}")

        results: list[dict[str, object]] = []
        layer_paths: dict[str, Path] = {}
        layer_records = tile["files"]
        if not isinstance(layer_records, dict):
            raise ValueError(f"{granule_id}: files must be an object")
        for layer, expected_member in expected_members.items():
            record = layer_records[layer]
            if not isinstance(record, dict):
                raise ValueError(f"{granule_id}: invalid {layer} file record")
            output_name = safe_filename(record["filename"])
            if output_name.lower() != expected_member.lower():
                raise ValueError(
                    f"{granule_id}: manifest filename for {layer} must be {expected_member}"
                )
            destination = raw_dir / "nasadem" / output_name
            info = member_by_layer[layer]
            if destination.exists():
                size, digest = verify_pinned(destination, record)
            else:
                temporary = destination.with_name(destination.name + ".part")
                try:
                    with source.open(info) as member, temporary.open("wb") as target:
                        shutil.copyfileobj(member, target, length=1024 * 1024)
                    size, digest = verify_pinned(temporary, record)
                    if size != info.file_size:
                        raise ValueError(
                            f"{output_name}: ZIP metadata says {info.file_size}, extracted {size}"
                        )
                    temporary.replace(destination)
                except Exception:
                    temporary.unlink(missing_ok=True)
                    raise
            results.append({"filename": output_name, "size_bytes": size, "sha256": digest})
            record["size_bytes"] = size
            record["sha256"] = digest
            layer_paths[layer] = destination

    tile["archive_size_bytes"] = archive_size
    tile["archive_sha256"] = archive_hash
    tile["observed_value_summary"] = inspect_nasadem_layers(layer_paths)
    return results


def download_nasadem(manifest: dict[str, object], raw_dir: Path) -> list[dict[str, object]]:
    tiles = manifest["nasadem"]["tiles"]
    missing_archives = [
        tile
        for tile in tiles
        if not (raw_dir / "nasadem" / safe_filename(tile["archive_filename"])).is_file()
    ]
    earthaccess = None
    if missing_archives:
        try:
            import earthaccess as earthaccess_module
        except ImportError as error:
            raise RuntimeError(
                "Install the data dependency group before NASADEM access: uv sync --group data"
            ) from error
        earthaccess = earthaccess_module
        auth = earthaccess.login(strategy="environment")
        if not auth.authenticated:
            raise RuntimeError("Earthdata authentication was not accepted")

    results = []
    for tile in tiles:
        granule_id = str(tile["granule_id"])
        archive_name = safe_filename(tile["archive_filename"])
        archive_path = raw_dir / "nasadem" / archive_name
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        if not archive_path.is_file():
            assert earthaccess is not None
            granules = earthaccess.search_data(
                short_name=str(manifest["nasadem"]["short_name"]),
                version=str(manifest["nasadem"]["collection_version"]),
                granule_name=granule_id,
                count=2,
            )
            if len(granules) != 1:
                raise ValueError(
                    f"{granule_id}: expected exactly one CMR granule, received {len(granules)}"
                )
            paths = earthaccess.download(granules, local_path=str(archive_path.parent))
            downloaded = [Path(item) for item in paths]
            matching = [item for item in downloaded if item.name == archive_name]
            if len(matching) != 1:
                names = ", ".join(item.name for item in downloaded)
                raise ValueError(
                    f"{granule_id}: expected archive {archive_name}; earthaccess returned {names}"
                )
            if matching[0] != archive_path:
                matching[0].replace(archive_path)
        file_results = validate_nasadem_products(tile, raw_dir)
        results.append({"granule_id": granule_id, "files": file_results})
        print(f"verified NASADEM {granule_id}: {archive_name}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download and verify K-017 NASADEM, ETOPO, GSHHG, and geoid assets."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--nasadem-only",
        action="store_true",
        help="Fetch only authenticated NASADEM granules; public files are left untouched.",
    )
    parser.add_argument(
        "--record-checksums",
        action="store_true",
        help="Write verified byte counts and SHA-256 values into the manifest.",
    )
    args = parser.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        args.output_dir.mkdir(parents=True, exist_ok=True)
        if not args.nasadem_only:
            for dataset in manifest["datasets"]:
                dataset_id = str(dataset["dataset_id"])
                subdir = {
                    "ETOPO_2022_v1_15s_surface": "etopo",
                    "GSHHG": "gshhg",
                    "PROJ_EGM_geoid_grids": "proj",
                }.get(dataset_id)
                if subdir is None:
                    continue
                output = args.output_dir / subdir
                output.mkdir(parents=True, exist_ok=True)
                for record in dataset.get("files", []):
                    size, digest = download_public_file(record, output)
                    record["size_bytes"] = size
                    record["sha256"] = digest
                    print(f"verified {record['filename']}: {size} bytes sha256={digest}")
                    if dataset_id == "GSHHG":
                        extract_gshhg_archive(
                            output / safe_filename(record["filename"]), output / "extracted"
                        )
        download_nasadem(manifest, args.output_dir)
        if args.record_checksums:
            args.manifest.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    except (KeyError, OSError, TypeError, ValueError, RuntimeError, URLError, zipfile.BadZipFile) as error:
        print(f"K-017 download failed: {error}", file=sys.stderr)
        return 1

    print(f"K-017 assets verified under {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
