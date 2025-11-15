"""Simple persistence for keeping track of the last sync timestamp."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class SyncState:
    """Represents persisted metadata for the sync process."""

    last_synced_at: Optional[datetime] = None

    @classmethod
    def load(cls, path: Path) -> "SyncState":
        if not path.exists():
            return cls()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return cls()
        last_synced_raw = payload.get("last_synced_at")
        if not last_synced_raw:
            return cls()
        try:
            return cls(last_synced_at=datetime.fromisoformat(last_synced_raw))
        except (TypeError, ValueError):
            return cls()

    def save(self, path: Path) -> None:
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
