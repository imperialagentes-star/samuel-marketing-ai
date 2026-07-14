from fastapi import APIRouter
from ..database import get_conn
from ..models import SettingsUpdate
from ..services.telegram_service import send_message
from ..services.scheduler import reschedule_from_settings

router = APIRouter()


@router.get("/")
def get_settings():
    conn = get_conn()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


@router.put("/")
def update_settings(s: SettingsUpdate):
    conn = get_conn()
    conn.execute("UPDATE settings SET value=? WHERE key='report_hour'", (str(s.report_hour),))
    conn.execute("UPDATE settings SET value=? WHERE key='report_minute'", (str(s.report_minute),))
    conn.execute("UPDATE settings SET value=? WHERE key='monitor_keywords'", (s.monitor_keywords,))
    conn.commit()
    conn.close()
    reschedule_from_settings()
    return {"ok": True}


@router.post("/test-telegram")
def test_telegram():
    ok = send_message(
        "✅ *Samuel Marketing AI*\n\nConexión con Telegram funcionando correctamente 🚀\n\nYa recibirás el reporte diario a las 8am."
    )
    return {"ok": ok}
