from datetime import datetime, timezone

from bank_sync.state_manager import SyncState


def test_sync_state_loads_from_missing_file(tmp_path):
    path = tmp_path / "state.json"
    state = SyncState.load(path)
    assert state.last_synced_at is None


def test_sync_state_save_and_load(tmp_path):
    path = tmp_path / "state.json"
    state = SyncState(last_synced_at=datetime(2023, 9, 1, tzinfo=timezone.utc))
    state.save(path)

    loaded = SyncState.load(path)
    assert loaded.last_synced_at == datetime(2023, 9, 1, tzinfo=timezone.utc)
