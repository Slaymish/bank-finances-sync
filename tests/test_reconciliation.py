import pytest

from bank_sync.reconciliation import ReconciliationResult, _latest_balance, reconcile


def test_reconcile_groups_by_account():
    transactions = [
        {"account": "Cheque", "amount": "10", "balance": "100", "date": "2023-09-01"},
        {"account": "Cheque", "amount": "-5", "balance": "", "date": "2023-09-02"},
        {"account": "Savings", "amount": "1", "balance": "50", "date": "2023-09-02"},
    ]
    results = reconcile(transactions)
    result_map = {r.account: r for r in results}
    assert isinstance(result_map["Cheque"], ReconciliationResult)
    assert result_map["Cheque"].sheet_balance == pytest.approx(5)
    assert result_map["Savings"].difference == pytest.approx(49)


def test_latest_balance_returns_zero_when_missing():
    transactions = [
        {"balance": "", "date": "2023-01-01"},
        {"balance": "not-a-number", "date": "2023-01-02"},
    ]
    assert _latest_balance(transactions) == 0.0
