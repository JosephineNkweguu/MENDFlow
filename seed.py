"""Create fictional demo records for screenshots and testing."""
from db import Repository


def seed_demo(repo: Repository):
    if repo.assets():
        return
    a1 = repo.add_asset({"asset_code":"HVAC-001","name":"Lobby Air Handler","category":"HVAC","location":"Main Lobby","status":"Active","notes":"Fictional demonstration asset."})
    a2 = repo.add_asset({"asset_code":"GEN-001","name":"Standby Generator","category":"Power","location":"Plant Room","status":"Active","notes":"Fictional demonstration asset."})
    repo.add_pm({"asset_id":a1,"task":"Inspect filters and belts","frequency":30,"frequency_unit":"days","next_due_date":"2026-10-15","status":"Scheduled"})
    repo.add_pm({"asset_id":a2,"task":"Run generator inspection","frequency":14,"frequency_unit":"days","next_due_date":"2026-10-20","status":"Scheduled"})
    repo.add_work_order({"asset_id":a1,"description":"Investigate unusual airflow noise","priority":"Medium","status":"Open","notes":"Fictional demonstration work order."})
    repo.add_work_order({"asset_id":a2,"description":"Replace worn battery terminals","priority":"High","status":"In Progress","notes":"Fictional demonstration work order."})


if __name__ == "__main__":
    repo = Repository()
    seed_demo(repo)
    print(f"Seeded {len(repo.assets())} assets, {len(repo.pm_schedules())} PM schedules, {len(repo.work_orders())} work orders.")
