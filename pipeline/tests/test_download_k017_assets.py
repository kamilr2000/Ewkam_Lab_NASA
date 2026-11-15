from __future__ import annotations

import hashlib
import io

from pipeline import download_k017_assets


def test_download_public_file_creates_missing_destination_directory(
    tmp_path, monkeypatch
) -> None:
    payload = b"synthetic pinned downloader test payload"
    record = {
        "filename": "sample.bin",
        "url": "https://example.invalid/sample.bin",
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    destination_dir = tmp_path / "data" / "raw" / "k042" / "etopo"
    assert not destination_dir.exists()

    monkeypatch.setattr(
        download_k017_assets,
        "urlopen",
        lambda request, timeout: io.BytesIO(payload),
    )

    size, digest = download_k017_assets.download_public_file(record, destination_dir)

    assert size == len(payload)
    assert digest == record["sha256"]
    assert (destination_dir / "sample.bin").read_bytes() == payload
    assert not (destination_dir / "sample.bin.part").exists()
