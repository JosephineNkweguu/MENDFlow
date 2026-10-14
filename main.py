"""MENDFlow MVP: preventive maintenance and work order management."""
from datetime import date
from nicegui import ui

from db import Repository
from reports import to_csv
from seed import seed_demo
from services import MENDFlowService
from validators import ASSET_STATUSES, PM_STATUSES, WORK_ORDER_PRIORITIES, WORK_ORDER_STATUSES

repo = Repository()
seed_demo(repo)
service = MENDFlowService(repo)

app_state = {"page": "Dashboard"}

def notify_error(exc):
    ui.notify(str(exc), type="negative", position="top")


def notify_saved(message):
    ui.notify(message, type="positive", position="top")


@ui.refreshable
def content():
    page = app_state["page"]
    if page == "Dashboard":
        dashboard()
    elif page == "Assets":
        assets_page()
    elif page == "PM Schedule":
        pm_page()
    elif page == "Work Orders":
        work_orders_page()
    else:
        reports_page()


def navigate(page: str):
    app_state["page"] = page
    content.refresh()


def shell():
    with ui.header().classes("items-center justify-between bg-[#153B50] text-white px-6"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("build_circle", size="32px")
            with ui.column().classes("gap-0"):
                ui.label("MENDFlow").classes("text-2xl font-bold tracking-wide")
                ui.label("PLAN • TRACK • MAINTAIN").classes("text-xs opacity-80")
        ui.label("Maintenance Management MVP").classes("text-sm opacity-90")
    with ui.left_drawer(value=True).classes("bg-white"):
        ui.label("MENDFlow").classes("text-xl font-bold text-[#153B50] px-3 pt-3")
        ui.label("Navigation").classes("text-xs text-gray-500 px-3")
        for item, icon in [("Dashboard", "dashboard"), ("Assets", "precision_manufacturing"), ("PM Schedule", "event_repeat"), ("Work Orders", "assignment"), ("Reports", "assessment")]:
            ui.button(item, icon=icon, on_click=lambda p=item: navigate(p)).props("flat align=left").classes("w-full justify-start")
        ui.separator()
        ui.label("Synthetic course data only").classes("text-xs text-gray-500 px-3")
    with ui.column().classes("w-full max-w-7xl mx-auto p-6"):
        content()


def dashboard():
    stats = repo.dashboard_stats()
    ui.label("Maintenance Overview").classes("text-3xl font-bold text-[#153B50]")
    ui.label("A focused MVP for assets, preventive maintenance, work orders, and basic reporting.").classes("text-gray-600 mb-4")
    with ui.row().classes("w-full gap-4 flex-wrap"):
        stat_card("Active Assets", stats["assets"], "precision_manufacturing")
        stat_card("Open Work Orders", stats["open_orders"], "assignment")
        stat_card("Overdue PM", stats["overdue_pm"], "warning")
        stat_card("Upcoming PM", stats["upcoming_pm"], "event")
    with ui.row().classes("w-full gap-4 items-stretch mt-4"):
        with ui.card().classes("flex-1"):
            ui.label("Recent Work Orders").classes("text-lg font-semibold")
            rows = repo.work_orders()[:5]
            ui.table(columns=[
                {"name":"id","label":"ID","field":"work_order_id"},
                {"name":"asset","label":"Asset","field":"asset_code"},
                {"name":"description","label":"Description","field":"description"},
                {"name":"priority","label":"Priority","field":"priority"},
                {"name":"status","label":"Status","field":"status"}], rows=rows, row_key="work_order_id").classes("w-full")
        with ui.card().classes("flex-1"):
            ui.label("Upcoming Preventive Maintenance").classes("text-lg font-semibold")
            rows = [r for r in repo.pm_schedules() if r["status"] == "Scheduled"][:5]
            ui.table(columns=[
                {"name":"asset","label":"Asset","field":"asset_code"},
                {"name":"task","label":"Task","field":"task"},
                {"name":"due","label":"Due","field":"next_due_date"},
                {"name":"status","label":"Status","field":"status"}], rows=rows, row_key="schedule_id").classes("w-full")


def stat_card(title, value, icon):
    with ui.card().classes("min-w-[220px] flex-1"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.column().classes("gap-0"):
                ui.label(title).classes("text-sm text-gray-500")
                ui.label(str(value)).classes("text-3xl font-bold text-[#153B50]")
            ui.icon(icon, size="38px").classes("text-[#1D6B5A]")


def assets_page():
    ui.label("Assets").classes("text-3xl font-bold text-[#153B50]")
    ui.label("Create, edit, search, and deactivate maintenance assets.").classes("text-gray-600")
    with ui.card().classes("w-full mt-4"):
        with ui.row().classes("w-full items-end"):
            code = ui.input("Asset code", placeholder="HVAC-003").classes("flex-1")
            name = ui.input("Asset name", placeholder="Roof-top unit").classes("flex-1")
            category = ui.input("Category").classes("flex-1")
            location = ui.input("Location").classes("flex-1")
            status = ui.select(ASSET_STATUSES, value="Active", label="Status").classes("w-36")
        notes = ui.textarea("Notes").classes("w-full")
        ui.button("Add Asset", icon="add", on_click=lambda: add_asset(code, name, category, location, status, notes), color="primary")
    with ui.card().classes("w-full mt-4"):
        ui.label("Asset Register").classes("text-lg font-semibold")
        search = ui.input("Search assets", placeholder="Code, name, category, location").classes("w-full")
        table_box = ui.column().classes("w-full")

        def refresh_table():
            table_box.clear()
            query = (search.value or "").lower().strip()
            rows = repo.assets()
            if query:
                rows = [r for r in rows if query in " ".join(str(r.get(k, "")) for k in ["asset_code","name","category","location"]).lower()]
            with table_box:
                ui.table(columns=[
                    {"name":"code","label":"Code","field":"asset_code","sortable":True},
                    {"name":"name","label":"Name","field":"name","sortable":True},
                    {"name":"category","label":"Category","field":"category"},
                    {"name":"location","label":"Location","field":"location"},
                    {"name":"status","label":"Status","field":"status"},
                ], rows=rows, row_key="asset_id").classes("w-full")
                for row in rows:
                    with ui.row().classes("items-center gap-2"):
                        ui.label(f"{row['asset_code']} • {row['name']}").classes("text-xs text-gray-500")
                        ui.button("Edit", icon="edit", on_click=lambda r=row: edit_asset_dialog(r)).props("flat dense")
        search.on("update:model-value", lambda _: refresh_table())
        refresh_table()


def add_asset(code, name, category, location, status, notes):
    try:
        service.create_asset(code.value, name.value, category.value, location.value, status.value, notes.value)
        notify_saved("Asset created.")
        navigate("Assets")
    except ValueError as exc:
        notify_error(exc)


def edit_asset_dialog(row):
    with ui.dialog() as dialog, ui.card().classes("w-[600px]"):
        ui.label("Edit Asset").classes("text-xl font-semibold")
        code = ui.input("Asset code", value=row["asset_code"]).classes("w-full")
        name = ui.input("Asset name", value=row["name"]).classes("w-full")
        category = ui.input("Category", value=row["category"]).classes("w-full")
        location = ui.input("Location", value=row["location"]).classes("w-full")
        status = ui.select(ASSET_STATUSES, value=row["status"], label="Status").classes("w-full")
        notes = ui.textarea("Notes", value=row["notes"]).classes("w-full")
        with ui.row().classes("justify-end"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", on_click=lambda: save_edit()).props("unelevated")

        def save_edit():
            try:
                service.update_asset(row["asset_id"], code.value, name.value, category.value, location.value, status.value, notes.value)
                dialog.close()
                notify_saved("Asset updated.")
                navigate("Assets")
            except ValueError as exc:
                notify_error(exc)
    dialog.open()


def pm_page():
    ui.label("Preventive Maintenance Schedule").classes("text-3xl font-bold text-[#153B50]")
    ui.label("Define recurring maintenance for existing assets and track completion.").classes("text-gray-600")
    assets = repo.assets()
    asset_options = {f"{a['asset_code']} • {a['name']}": a["asset_id"] for a in assets}
    with ui.card().classes("w-full mt-4"):
        asset = ui.select(asset_options, label="Asset").classes("w-full")
        task = ui.input("Maintenance task", placeholder="Inspect filters and belts").classes("w-full")
        with ui.row().classes("w-full"):
            frequency = ui.number("Frequency", min=1, step=1, value=30).classes("flex-1")
            unit = ui.select(["days", "weeks", "months"], value="days", label="Unit").classes("flex-1")
            due = ui.date(value=date.today().isoformat()).classes("flex-1")
            status = ui.select(PM_STATUSES, value="Scheduled", label="Status").classes("flex-1")
        ui.button("Save Schedule", icon="save", on_click=lambda: add_pm(asset, task, frequency, unit, due, status))
    with ui.card().classes("w-full mt-4"):
        ui.label("PM Schedule").classes("text-lg font-semibold")
        rows = repo.pm_schedules()
        ui.table(columns=[
            {"name":"asset","label":"Asset","field":"asset_code"},
            {"name":"task","label":"Task","field":"task"},
            {"name":"frequency","label":"Frequency","field":"frequency"},
            {"name":"due","label":"Next Due","field":"next_due_date","sortable":True},
            {"name":"status","label":"Status","field":"status"},
        ], rows=rows, row_key="schedule_id").classes("w-full")
        for row in rows:
            if row["status"] == "Scheduled":
                ui.button(f"Mark Complete: {row['asset_code']} / {row['task']}", icon="check", on_click=lambda r=row: complete_pm(r)).props("flat")


def add_pm(asset, task, frequency, unit, due, status):
    try:
        service.create_pm(asset.value, task.value, frequency.value, unit.value, due.value, status.value)
        notify_saved("Preventive maintenance schedule created.")
        navigate("PM Schedule")
    except ValueError as exc:
        notify_error(exc)


def complete_pm(row):
    try:
        service.complete_pm(row["schedule_id"])
        notify_saved("Preventive maintenance marked complete and added to history.")
        navigate("PM Schedule")
    except ValueError as exc:
        notify_error(exc)


def work_orders_page():
    ui.label("Work Orders").classes("text-3xl font-bold text-[#153B50]")
    ui.label("Create and manage maintenance work using the approved core workflow.").classes("text-gray-600")
    assets = repo.assets()
    asset_options = {f"{a['asset_code']} • {a['name']}": a["asset_id"] for a in assets}
    with ui.card().classes("w-full mt-4"):
        asset = ui.select(asset_options, label="Existing asset").classes("w-full")
        description = ui.textarea("Maintenance description").classes("w-full")
        with ui.row().classes("w-full"):
            priority = ui.select(WORK_ORDER_PRIORITIES, value="Medium", label="Priority").classes("flex-1")
            status = ui.select(WORK_ORDER_STATUSES, value="Open", label="Status").classes("flex-1")
        notes = ui.textarea("Notes").classes("w-full")
        ui.button("Create Work Order", icon="add_task", on_click=lambda: add_work_order(asset, description, priority, status, notes))
    with ui.card().classes("w-full mt-4"):
        ui.label("Work Order Register").classes("text-lg font-semibold")
        rows = repo.work_orders()
        ui.table(columns=[
            {"name":"id","label":"ID","field":"work_order_id","sortable":True},
            {"name":"asset","label":"Asset","field":"asset_code"},
            {"name":"description","label":"Description","field":"description"},
            {"name":"priority","label":"Priority","field":"priority"},
            {"name":"status","label":"Status","field":"status"},
        ], rows=rows, row_key="work_order_id").classes("w-full")
        for row in rows:
            with ui.row().classes("items-center"):
                ui.label(f"WO-{row['work_order_id']:03d} • {row['asset_code']}").classes("text-xs text-gray-500")
                if row["status"] != "Completed":
                    ui.button("In Progress", on_click=lambda r=row: change_wo(r, "In Progress")).props("flat dense")
                    ui.button("Complete", on_click=lambda r=row: change_wo(r, "Completed")).props("flat dense")


def add_work_order(asset, description, priority, status, notes):
    try:
        service.create_work_order(asset.value, description.value, priority.value, status.value, notes.value)
        notify_saved("Work order created.")
        navigate("Work Orders")
    except ValueError as exc:
        notify_error(exc)


def change_wo(row, status):
    try:
        service.update_work_order_status(row["work_order_id"], status)
        notify_saved(f"Work order updated to {status}.")
        navigate("Work Orders")
    except ValueError as exc:
        notify_error(exc)


def reports_page():
    ui.label("Reports").classes("text-3xl font-bold text-[#153B50]")
    ui.label("Basic operational reports based on persistent SQLite data.").classes("text-gray-600")
    pm_rows = repo.report_pm()
    wo_rows = repo.report_work_orders()
    with ui.card().classes("w-full mt-4"):
        ui.label("Preventive Maintenance Compliance").classes("text-lg font-semibold")
        ui.button("Download PM CSV", icon="download", on_click=lambda: download_pm(pm_rows)).props("flat")
        ui.table(columns=[
            {"name":"asset","label":"Asset","field":"asset_code"},
            {"name":"name","label":"Name","field":"asset_name"},
            {"name":"task","label":"Task","field":"task"},
            {"name":"due","label":"Next Due","field":"next_due_date"},
            {"name":"status","label":"Status","field":"status"}], rows=pm_rows).classes("w-full")
    with ui.card().classes("w-full mt-4"):
        ui.label("Work Order Status Report").classes("text-lg font-semibold")
        ui.button("Download Work Order CSV", icon="download", on_click=lambda: download_wo(wo_rows)).props("flat")
        ui.table(columns=[
            {"name":"id","label":"ID","field":"work_order_id"},
            {"name":"asset","label":"Asset","field":"asset_code"},
            {"name":"description","label":"Description","field":"description"},
            {"name":"priority","label":"Priority","field":"priority"},
            {"name":"status","label":"Status","field":"status"}], rows=wo_rows).classes("w-full")


def download_pm(rows):
    csv = to_csv(rows, [("asset_code","Asset"),("asset_name","Name"),("task","Task"),("next_due_date","Next Due"),("status","Status")])
    ui.download.content(csv, "mendflow_pm_report.csv", "text/csv")


def download_wo(rows):
    csv = to_csv(rows, [("work_order_id","ID"),("asset_code","Asset"),("description","Description"),("priority","Priority"),("status","Status")])
    ui.download.content(csv, "mendflow_work_order_report.csv", "text/csv")


@ui.page("/")
def index():
    ui.colors(primary="#153B50", secondary="#F2B705", accent="#1D6B5A")
    ui.query("body").classes("bg-slate-50")
    ui.page_title("MENDFlow | Plan • Track • Maintain")
    shell()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="MENDFlow", port=8080, reload=False)
