from db import Repository
from services import MENDFlowService


def test_repository_persistence(tmp_path):
    repo = Repository(tmp_path / "test.db")
    service = MENDFlowService(repo)
    service.create_asset("P-001", "Test Pump", "Mechanical", "Plant Room", "Active", "Synthetic")
    rows = repo.assets()
    assert len(rows) == 1
    assert rows[0]["asset_code"] == "P-001"


def test_work_order_uses_existing_asset(tmp_path):
    repo = Repository(tmp_path / "test.db")
    service = MENDFlowService(repo)
    asset_id = service.create_asset("P-001", "Test Pump", "Mechanical", "Plant Room", "Active", "Synthetic")
    wo_id = service.create_work_order(asset_id, "Inspect seal", "Medium", "Open", "Synthetic")
    assert repo.work_orders()[0]["work_order_id"] == wo_id
