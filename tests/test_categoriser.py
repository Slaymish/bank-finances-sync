from categoriser import Categoriser


def test_categoriser_applies_highest_priority_match():
    rules = [
        {"pattern": "countdown", "category": "Groceries", "priority": 50},
        {"pattern": "count", "category": "Misc", "priority": 100},
    ]
    categoriser = Categoriser(rules)
    txn = {"merchant_normalised": "Countdown Ponsonby"}
    assert categoriser.categorise(txn) == "Groceries"


def test_categoriser_skips_empty_patterns():
    rules = [
        {"pattern": "", "category": "Ignored"},
        {"pattern": "ferry", "category": "Transport"},
    ]
    categoriser = Categoriser(rules)
    assert categoriser.categorise({"merchant_normalised": "Ferry ride"}) == "Transport"


def test_detect_transfer_checks_multiple_fields():
    txn = {"description_raw": "Internal Transfer", "merchant_normalised": "BNZ"}
    assert Categoriser.detect_transfer(txn) is True
    assert Categoriser.detect_transfer({"description_raw": "Cafe"}) is False
