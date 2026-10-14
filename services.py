"""Application services: business workflows between UI and repository."""
from datetime import date
from db import Repository
from validators import validate_asset, validate_pm, validate_work_order


class MENDFlowService:
    def __init__(self, repository: Repository):
        self.repo = repository

    def create_asset(self, code, name, category, location, status, notes):
        code, name, status = validate_asset(code, name, status)
        try:
            return self.repo.add_asset({"asset_code": code, "name": name, "category": category, "location": location, "status": status, "notes": notes})
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise ValueError("Asset code already exists.") from exc
            raise

    def update_asset(self, asset_id, code, name, category, location, status, notes):
        code, name, status = validate_asset(code, name, status)
        self.repo.update_asset(asset_id, {"asset_code": code, "name": name, "category": category, "location": location, "status": status, "notes": notes})

    def create_pm(self, asset_id, task, frequency, frequency_unit, due_date, status):
        asset_id, task, frequency, due_date, status = validate_pm(asset_id, task, frequency, due_date, status)
        if not self.repo.asset_exists(asset_id):
            raise ValueError("Selected asset does not exist.")
        return self.repo.add_pm({"asset_id": asset_id, "task": task, "frequency": frequency, "frequency_unit": frequency_unit, "next_due_date": due_date, "status": status})

    def create_work_order(self, asset_id, description, priority, status, notes):
        asset_id, description, priority, status = validate_work_order(asset_id, description, priority, status)
        if not self.repo.asset_exists(asset_id):
            raise ValueError("Selected asset does not exist.")
        return self.repo.add_work_order({"asset_id": asset_id, "description": description, "priority": priority, "status": status, "notes": notes})

    def update_work_order_status(self, work_order_id, status):
        self.repo.update_work_order_status(work_order_id, status, date.today().isoformat())

    def complete_pm(self, schedule_id):
        self.repo.complete_pm(schedule_id, date.today().isoformat())
