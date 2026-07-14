from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .market_monitor import generate_daily_report
from .telegram_service import send_message
from ..database import get_conn

_scheduler = BackgroundScheduler(timezone="America/Bogota")


def _get_setting(key: str) -> str:
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else ""


def run_daily_report():
    keywords = [k.strip() for k in _get_setting("monitor_keywords").split(",") if k.strip()]
    report = generate_daily_report(keywords)
    send_message(report)
    conn = get_conn()
    conn.execute("INSERT INTO reports (type, title, content) VALUES (?, ?, ?)",
                 ("daily", "Reporte diario automático", report))
    conn.commit()
    conn.close()


def _reschedule():
    hour = int(_get_setting("report_hour") or "8")
    minute = int(_get_setting("report_minute") or "0")
    _scheduler.add_job(
        run_daily_report,
        CronTrigger(hour=hour, minute=minute),
        id="daily_report",
        replace_existing=True,
    )


def start_scheduler():
    _reschedule()
    if not _scheduler.running:
        _scheduler.start()


def stop_scheduler():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)


def is_monitor_active() -> bool:
    return _get_setting("monitor_active") == "true"


def set_monitor_active(active: bool):
    conn = get_conn()
    conn.execute("UPDATE settings SET value=? WHERE key='monitor_active'",
                 ("true" if active else "false",))
    conn.commit()
    conn.close()
    if active:
        _reschedule()
    else:
        job = _scheduler.get_job("daily_report")
        if job:
            job.pause()


def trigger_report_now() -> str:
    keywords = [k.strip() for k in _get_setting("monitor_keywords").split(",") if k.strip()]
    report = generate_daily_report(keywords)
    send_message(report)
    conn = get_conn()
    conn.execute("INSERT INTO reports (type, title, content) VALUES (?, ?, ?)",
                 ("daily", "Reporte manual", report))
    conn.commit()
    conn.close()
    return report


def reschedule_from_settings():
    _reschedule()
