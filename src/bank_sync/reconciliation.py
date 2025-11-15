"""Simple reconciliation helpers."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class ReconciliationResult:
    account: str
    difference: float
    expected_balance: float
    sheet_balance: float

    @property
    def is_ok(self) -> bool:
        return abs(self.difference) < 0.10  # 10 cent tolerance for rounding/timing differences


def reconcile(transactions: Iterable[dict]) -> List[ReconciliationResult]:
    grouped: Dict[str, List[dict]] = defaultdict(list)
    for txn in transactions:
        grouped[txn.get("account", "unknown")].append(txn)

    results: List[ReconciliationResult] = []
    for account, account_transactions in grouped.items():
        sheet_balance = sum(float(txn.get("amount", 0)) for txn in account_transactions)
        expected_balance = _latest_balance(account_transactions)
        difference = (expected_balance or 0) - sheet_balance
        results.append(
            ReconciliationResult(
                account=account,
                difference=difference,
                expected_balance=expected_balance or 0,
                sheet_balance=sheet_balance,
            )
        )
    return results


def _latest_balance(transactions: List[dict]) -> float:
    sorted_txn = sorted(transactions, key=lambda t: t.get("date", ""))
    for txn in reversed(sorted_txn):
        if txn.get("balance"):
            try:
                return float(txn["balance"])
            except (KeyError, ValueError, TypeError):
                continue
    return 0.0
