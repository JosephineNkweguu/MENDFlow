from validators import validate_asset, validate_pm, validate_work_order


def test_asset_validation():
    assert validate_asset("A-001", "Pump", "Active") == ("A-001", "Pump", "Active")


def test_asset_requires_code():
    try:
        validate_asset("", "Pump", "Active")
        assert False
    except ValueError as exc:
        assert "Asset code" in str(exc)


def test_pm_requires_positive_frequency():
    try:
        validate_pm(1, "Inspect", 0, "2026-10-01", "Scheduled")
        assert False
    except ValueError as exc:
        assert "greater than zero" in str(exc)


def test_work_order_validation():
    result = validate_work_order(1, "Repair pump", "High", "Open")
    assert result == (1, "Repair pump", "High", "Open")
