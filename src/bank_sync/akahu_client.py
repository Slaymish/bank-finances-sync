"""Client utilities for interacting with the Akahu API."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional

import requests

LOGGER = logging.getLogger(__name__)


@dataclass
class AkahuTransaction:
    """Representation of a transaction returned from Akahu."""

    id: str
    date: str
    account: str
    amount: float
    balance: Optional[float]
    description_raw: str
    merchant_normalised: str
    source: str

    @classmethod
    def from_payload(cls, payload: Dict, *, source: str, account_name: str = "unknown") -> "AkahuTransaction":
        """Create an :class:`AkahuTransaction` from an Akahu API payload."""

        settled_at = payload.get("date") or payload.get("settled_at")
        merchant = payload.get("merchant") or {}
        return cls(
            id=payload["_id"],
            date=_ensure_iso_date(settled_at),
            account=account_name,
            amount=float(payload.get("amount", 0)),
            balance=_safe_float(payload.get("balance")),
            description_raw=payload.get("description", ""),
            merchant_normalised=merchant.get("name", "").strip() or payload.get("merchant_name", ""),
            source=source,
        )

    def to_row(self, *, category: str, category_type: str, is_transfer: bool, imported_at: datetime) -> List[str]:
        """Return the row representation expected by Google Sheets."""

        return [
            self.id,
            self.date,
            self.account,
            f"{self.amount:.2f}",
            "" if self.balance is None else f"{self.balance:.2f}",
            self.description_raw,
            self.merchant_normalised,
            category,
            category_type,
            str(is_transfer).upper(),
            self.source,
            imported_at.isoformat(),
        ]


def _safe_float(value: Optional[float]) -> Optional[float]:
    try:
        return None if value is None else float(value)
    except (ValueError, TypeError):
        return None


def _ensure_iso_date(raw: Optional[str]) -> str:
    if not raw:
        return date.today().isoformat()
    if len(raw) == 10:
        return raw
    try:
        return datetime.fromisoformat(raw).date().isoformat()
    except ValueError:
        return date.today().isoformat()


class AkahuClient:
    """Minimal HTTP client for the Akahu API."""

    def __init__(
        self,
        *,
        user_token: str,
        app_token: str,
        base_url: str = "https://api.akahu.io/v1",
        session: Optional[requests.Session] = None,
    ) -> None:
        self._user_token = user_token
        self._app_token = app_token
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._account_map: Optional[Dict[str, str]] = None

    def _get_account_map(self) -> Dict[str, str]:
        """Fetch accounts and return ID -> name mapping."""
        if self._account_map is None:
            payload = self._request("GET", "/accounts")
            self._account_map = {
                account["_id"]: account.get("name", "unknown")
                for account in payload.get("items", [])
            }
            LOGGER.info("Loaded %d accounts", len(self._account_map))
        return self._account_map

    def fetch_settled_transactions(
        self,
        *,
        start_datetime: datetime,
        end_datetime: datetime,
        page_size: int = 250,
    ) -> Iterable[AkahuTransaction]:
        """Yield all settled transactions within the given dates."""

        params = {
            "start": start_datetime.isoformat(),
            "end": end_datetime.isoformat(),
            "limit": page_size,
            "type": "SETTLED",
        }
        cursor: Optional[str] = None
        account_map = self._get_account_map()

        while True:
            payload = self._request("GET", "/transactions", params={**params, "cursor": cursor} if cursor else params)
            items = payload.get("items", [])
            LOGGER.info("Akahu API returned %d items (all settled via type filter)", len(items))
            for transaction in items:
                account_id = transaction.get("_account", "")
                account_name = account_map.get(account_id, "unknown")
                yield AkahuTransaction.from_payload(transaction, source="akahu_bnz", account_name=account_name)

            cursor = payload.get("cursor", {}).get("next")
            if not cursor:
                break

    def _request(self, method: str, path: str, *, params: Optional[Dict] = None) -> Dict:
        url = f"{self._base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self._user_token}",
            "X-Akahu-Id": self._app_token,
        }
        LOGGER.debug("Akahu request %s %s params=%s", method, url, params)
        response = self._session.request(method, url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
