"""Reusable validation rules for MENDFlow."""

ASSET_STATUSES = ["Active", "Inactive"]
PM_STATUSES = ["Scheduled", "Completed", "Paused"]
WORK_ORDER_PRIORITIES = ["Low", "Medium", "High", "Critical"]
WORK_ORDER_STATUSES = ["Open", "In Progress", "Completed", "Cancelled"]


def required(value: str, field: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{field} is required.")
    return value


def positive_number(value, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be a whole number greater than zero.")
    if number <= 0:
        raise ValueError(f"{field} must be greater than zero.")
    return number


def one_of(value: str, choices: list[str], field: str) -> str:
    if value not in choices:
        raise ValueError(f"{field} must be one of: {', '.join(choices)}.")
    return value


def validate_asset(code: str, name: str, status: str) -> tuple[str, str, str]:
    return required(code, "Asset code"), required(name, "Asset name"), one_of(status, ASSET_STATUSES, "Status")


def validate_pm(asset_id, task: str, frequency, due_date: str, status: str):
    if not asset_id:
        raise ValueError("An existing asset is required.")
    return int(asset_id), required(task, "Maintenance task"), positive_number(frequency, "Frequency"), required(due_date, "Next due date"), one_of(status, PM_STATUSES, "Status")


def validate_work_order(asset_id, description: str, priority: str, status: str):
    if not asset_id:
        raise ValueError("An existing asset is required.")
    return int(asset_id), required(description, "Description"), one_of(priority, WORK_ORDER_PRIORITIES, "Priority"), one_of(status, WORK_ORDER_STATUSES, "Status")
