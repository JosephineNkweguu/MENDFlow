"""SQLite repository for MENDFlow. All database access is centralized here."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mendflow.db"

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'Active',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS pm_schedules (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    task TEXT NOT NULL,
    frequency INTEGER NOT NULL,
    frequency_unit TEXT NOT NULL DEFAULT 'days',
    next_due_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Scheduled',
    last_completed TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS work_orders (
    work_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open',
    notes TEXT,
    opened_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS maintenance_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    work_order_id INTEGER,
    activity_type TEXT NOT NULL,
    activity_date TEXT NOT NULL,
    details TEXT,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
    FOREIGN KEY(work_order_id) REFERENCES work_orders(work_order_id) ON DELETE SET NULL
);
"""


class Repository:
    """Reusable data-access component; UI and services never execute SQL directly."""

    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self):
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def execute(self, sql: str, params: tuple = ()) -> int:
        with self.connect() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid

    def fetch_all(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self.connect() as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def fetch_one(self, sql: str, params: tuple = ()) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(sql, params).fetchone()
            return dict(row) if row else None

    def asset_exists(self, asset_id: int) -> bool:
        return self.fetch_one("SELECT 1 FROM assets WHERE asset_id = ?", (asset_id,)) is not None

    def assets(self):
        return self.fetch_all("SELECT * FROM assets ORDER BY asset_code")

    def get_asset(self, asset_id: int):
        return self.fetch_one("SELECT * FROM assets WHERE asset_id = ?", (asset_id,))

    def add_asset(self, data: dict) -> int:
        return self.execute("""INSERT INTO assets(asset_code,name,category,location,status,notes) VALUES(?,?,?,?,?,?)""",
                            (data["asset_code"], data["name"], data.get("category", ""), data.get("location", ""), data["status"], data.get("notes", "")))

    def update_asset(self, asset_id: int, data: dict):
        self.execute("""UPDATE assets SET asset_code=?,name=?,category=?,location=?,status=?,notes=?,updated_at=CURRENT_TIMESTAMP WHERE asset_id=?""",
                     (data["asset_code"], data["name"], data.get("category", ""), data.get("location", ""), data["status"], data.get("notes", ""), asset_id))

    def pm_schedules(self):
        return self.fetch_all("""SELECT p.*, a.asset_code, a.name AS asset_name FROM pm_schedules p JOIN assets a ON a.asset_id=p.asset_id ORDER BY p.next_due_date""")

    def add_pm(self, data: dict) -> int:
        return self.execute("""INSERT INTO pm_schedules(asset_id,task,frequency,frequency_unit,next_due_date,status) VALUES(?,?,?,?,?,?)""",
                            (data["asset_id"], data["task"], data["frequency"], data.get("frequency_unit", "days"), data["next_due_date"], data["status"]))

    def complete_pm(self, schedule_id: int, date: str):
        with self.connect() as conn:
            row = conn.execute("SELECT asset_id, task FROM pm_schedules WHERE schedule_id=?", (schedule_id,)).fetchone()
            if not row:
                raise ValueError("Preventive maintenance schedule was not found.")
            conn.execute("UPDATE pm_schedules SET status='Completed', last_completed=? WHERE schedule_id=?", (date, schedule_id))
            conn.execute("INSERT INTO maintenance_history(asset_id, activity_type, activity_date, details) VALUES(?,?,?,?)",
                         (row["asset_id"], "Preventive Maintenance", date, row["task"]))
            conn.commit()

    def work_orders(self):
        return self.fetch_all("""SELECT w.*, a.asset_code, a.name AS asset_name FROM work_orders w JOIN assets a ON a.asset_id=w.asset_id ORDER BY w.opened_at DESC""")

    def add_work_order(self, data: dict) -> int:
        return self.execute("""INSERT INTO work_orders(asset_id,description,priority,status,notes) VALUES(?,?,?,?,?)""",
                            (data["asset_id"], data["description"], data["priority"], data["status"], data.get("notes", "")))

    def update_work_order_status(self, work_order_id: int, status: str, date: str):
        with self.connect() as conn:
            row = conn.execute("SELECT asset_id, description FROM work_orders WHERE work_order_id=?", (work_order_id,)).fetchone()
            if not row:
                raise ValueError("Work order was not found.")
            completed_at = date if status == "Completed" else None
            conn.execute("UPDATE work_orders SET status=?, completed_at=? WHERE work_order_id=?", (status, completed_at, work_order_id))
            conn.execute("INSERT INTO maintenance_history(asset_id, work_order_id, activity_type, activity_date, details) VALUES(?,?,?,?,?)",
                         (row["asset_id"], work_order_id, "Work Order", date, f"{status}: {row['description']}"))
            conn.commit()

    def history_for_asset(self, asset_id: int):
        return self.fetch_all("SELECT * FROM maintenance_history WHERE asset_id=? ORDER BY activity_date DESC, history_id DESC", (asset_id,))

    def dashboard_stats(self):
        return {
            "assets": self.fetch_one("SELECT COUNT(*) c FROM assets WHERE status='Active'")["c"],
            "open_orders": self.fetch_one("SELECT COUNT(*) c FROM work_orders WHERE status IN ('Open','In Progress')")["c"],
            "overdue_pm": self.fetch_one("SELECT COUNT(*) c FROM pm_schedules WHERE status='Scheduled' AND date(next_due_date) < date('now')")["c"],
            "upcoming_pm": self.fetch_one("SELECT COUNT(*) c FROM pm_schedules WHERE status='Scheduled' AND date(next_due_date) >= date('now') AND date(next_due_date) <= date('now','+30 day')")["c"],
        }

    def report_pm(self):
        return self.fetch_all("""SELECT a.asset_code, a.name AS asset_name, p.task, p.next_due_date, p.status, p.last_completed
                               FROM pm_schedules p JOIN assets a ON a.asset_id=p.asset_id ORDER BY p.next_due_date""")

    def report_work_orders(self):
        return self.fetch_all("""SELECT w.work_order_id, a.asset_code, a.name AS asset_name, w.description, w.priority, w.status, w.opened_at, w.completed_at
                               FROM work_orders w JOIN assets a ON a.asset_id=w.asset_id ORDER BY w.opened_at DESC""")
