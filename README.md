# MENDFlow

**Preventive Maintenance & Work Order Management System**

MENDFlow is a focused software-development capstone project for SDEV-435 Applied Software Practice I. The MVP is designed for small property owners, property managers, and facilities personnel who need a central place to manage assets, preventive maintenance schedules, work orders, and basic maintenance reports.

## Current MVP

- Asset creation, editing, search, and status management
- Preventive maintenance scheduling and completion tracking
- Work-order creation and status updates
- Maintenance history generated from completed PM and work-order activity
- Basic PM and work-order reports
- CSV report export
- Persistent SQLite storage
- Reusable validation, repository, service, and CSV-reporting components
- Fictional synthetic demonstration data

## Technology

- Python
- NiceGUI
- SQLite
- Git/GitHub
- pytest

## Architecture

`NiceGUI UI → Application Services → Validation → Repository → SQLite`

The repository is the only component that performs database reads and writes. Application services coordinate business workflows, while reusable validators enforce approved input rules.

## Run locally

1. Create a virtual environment.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Start the application:

```bash
python main.py
```

4. Open `http://localhost:8080` in a browser.

The first run creates `data/mendflow.db` and inserts fictional demo records if the database is empty.

## Test

```bash
pytest -q
```

## Data stewardship

The repository is intended for course demonstration. It contains fictional synthetic data only. Do not add client names, credentials, private operational details, or proprietary maintenance records.

## Scope control

The MVP remains limited to asset management, preventive maintenance scheduling, work orders, and basic reporting. Inventory management, purchasing, automated notifications, advanced analytics, multi-property support, and other larger enhancements remain outside the current course scope.
