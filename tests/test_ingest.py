# test/test_ingest.py
import json

from src.etl import ingest


def test_ingest_creat_files(tmp_path):
    urls = tmp_path / "urls.txt"
    urls.write_text("https://example.com/test\n")
    ingest.main(str(urls), str(tmp_path))
    files = list(tmp_path.glob("*.json"))
    assert files
    data = json.loads(files[0].read_text())
    assert {"video_id", "transcript", "predictions","claims","evidence"}.issubset(data)
