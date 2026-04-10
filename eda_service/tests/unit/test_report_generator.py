import io
import zipfile
from pathlib import Path
import pytest
from app.service.report_generator import _sha256_hex
from app.service.report_generator import ReportGenerator
from app.domain.exceptions import FileNotFoundInArchiveError
from app.domain.entities import Report, FileInfo, DatasetInfo
from app.domain.exceptions import DatasetArchiveDownloadError


def _make_zip_bytes(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_generator_hash_is_sha256_lowercase():
    """Проверяет, что хеш вычисляется как sha256(...).hexdigest().lower()"""

    h = _sha256_hex(b"ABC")
    assert h == h.lower()
    assert len(h) == 64


def test_generator_path_matching_exact_vs_basename_unique(tmp_path: Path):
    """Проверяет поиск файла в распаковке"""

    extract_dir = tmp_path / "extract"
    (extract_dir / "a").mkdir(parents=True)
    (extract_dir / "b").mkdir(parents=True)
    (extract_dir / "a" / "data.csv").write_text("1,2\n")
    (extract_dir / "b" / "data.csv").write_text("3,4\n")
    (extract_dir / "c.csv").write_text("5,6\n")

    gen = ReportGenerator(storage=None)

    p = gen._find_file_in_extracted_dir(extract_dir, "c.csv")
    assert p is not None and p.name == "c.csv"

    p2 = gen._find_file_in_extracted_dir(extract_dir, "data.csv")
    assert p2 is None

    p3 = gen._find_file_in_extracted_dir(extract_dir, "a/data.csv")
    assert p3 is not None and p3.as_posix().endswith("a/data.csv")


@pytest.mark.asyncio
async def test_generator_file_not_in_archive_422(monkeypatch, tmp_path: Path):
    """Проверяет: файла нет в архиве"""

    zip_bytes = _make_zip_bytes({"other.csv": b"a,b\n1,2\n"})

    async def fake_download(_url: str, target_path: Path) -> None:
        target_path.write_bytes(zip_bytes)

    gen = ReportGenerator(storage=None)
    monkeypatch.setattr(gen, "_download_zip", fake_download)

    report = Report(report_id=1, file_id=1, status="processing")
    file_info = FileInfo(file_id=1, dataset_id=1, file_name="missing.csv", file_hash="x")
    dataset_info = DatasetInfo(dataset_id=1, download_url="http://x")

    with pytest.raises(FileNotFoundInArchiveError):
        await gen.compute_input_file_hash_from_dataset_zip(file_info=file_info, dataset_info=dataset_info)


@pytest.mark.asyncio
async def test_generator_download_zip_failure_503(monkeypatch):
    """Проверяет: ZIP не скачивается"""

    gen = ReportGenerator(storage=None)

    async def fail_download(_url, _target):
        raise DatasetArchiveDownloadError(
            dataset_id=1, download_url="http://x", reason="HTTP 500"
        )

    monkeypatch.setattr(gen, "_download_zip", fail_download)

    file_info = FileInfo(file_id=1, dataset_id=1, file_name="data.csv", file_hash="x")
    dataset_info = DatasetInfo(dataset_id=1, download_url="http://x")

    with pytest.raises(DatasetArchiveDownloadError):
        await gen.compute_input_file_hash_from_dataset_zip(file_info=file_info, dataset_info=dataset_info)