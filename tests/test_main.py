from main import _needs_update, load_config
from sheets_client import TRANSACTION_HEADERS


def test_load_config_reads_file(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"key": 1}')
    config = load_config(path)
    assert config == {"key": 1}


def test_needs_update_detects_differences():
    existing = dict(zip(TRANSACTION_HEADERS, ["a"] * len(TRANSACTION_HEADERS)))
    new_row = ["a"] * len(TRANSACTION_HEADERS)
    assert _needs_update(existing, new_row) is False
    new_row[3] = "different"
    assert _needs_update(existing, new_row) is True
