from fastapi import APIRouter
from ..database import get_conn
from ..services.scheduler import is_monitor_active, set_monitor_active, trigger_report_now

router = APIRouter()


@router.get("/status")
def monitor_status():
    conn = get_conn()
    reports = conn.execute(
        "SELECT id, type, title, created_at FROM reports ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return {"active": is_monitor_active(), "recent_reports": [dict(r) for r in reports]}


@router.post("/start")
def start_monitor():
    set_monitor_active(True)
    return {"ok": True, "active": True}


@router.post("/stop")
def stop_monitor():
    set_monitor_active(False)
    return {"ok": True, "active": False}


@router.post("/run-now")
def run_now():
    report = trigger_report_now()
    return {"ok": True, "report": report}


@router.get("/reports")
def list_reports(limit: int = 30):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
