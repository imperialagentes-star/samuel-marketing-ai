from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
import sys
import os
import logging
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

LOG_PATH = ROOT / "data" / "app.log"
LOG_PATH.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_PATH), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

from backend.database import init_db
from backend.services.scheduler import start_scheduler, stop_scheduler
from backend.routers import clients, monitor, modules, settings, logs, workflows


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Samuel Marketing AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        password = os.getenv("APP_PASSWORD", "samuel2026")
        token = request.headers.get("X-App-Password", "")
        if token != password:
            return JSONResponse({"error": "No autorizado"}, status_code=401)
    return await call_next(request)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["monitor"])
app.include_router(modules.router, prefix="/api/modules", tags=["modules"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])

DASHBOARD = ROOT / "dashboard"
app.mount("/", StaticFiles(directory=str(DASHBOARD), html=True), name="dashboard")
