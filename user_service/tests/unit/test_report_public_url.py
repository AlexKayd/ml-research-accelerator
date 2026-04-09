from app.core.report_public_url import build_report_public_url


def test_list_reports_builds_report_url_from_minio_public_base():
    """Проверяет сборку публичной ссылки на отчёт из base/bucket/key"""
    url = build_report_public_url(
        public_base_url="http://minio.test",
        bucket_name="reports",
        object_key="u/1/r/10.html",
    )
    assert url == "http://minio.test/reports/u/1/r/10.html"


def test_build_report_public_url_returns_none_when_missing_parts():
    """Проверяет, что если части URL отсутствуют возвращается None"""
    assert build_report_public_url("http://minio.test", None, "a") is None
    assert build_report_public_url("http://minio.test", "b", None) is None
    assert build_report_public_url("", "b", "k") is None