from fastapi import APIRouter
from pathlib import Path
import re

router = APIRouter()

LOG_FILE = Path(__file__).parent.parent.parent / "data" / "app.log"


@router.get("/")
def get_logs(limit: int = 200):
    if not LOG_FILE.exists():
        return {"lines": []}
    try:
        text = LOG_FILE.read_text(encoding="utf-8", errors="replace")
        lines = text.strip().splitlines()[-limit:]
        parsed = []
        for line in lines:
            level = "INFO"
            if "ERROR" in line:
                level = "ERROR"
            elif "WARNING" in line or "WARN" in line:
                level = "WARNING"
            elif "DEBUG" in line:
                level = "DEBUG"
            parsed.append({"raw": line, "level": level})
        return {"lines": parsed}
    except Exception as e:
        return {"lines": [{"raw": str(e), "level": "ERROR"}]}
