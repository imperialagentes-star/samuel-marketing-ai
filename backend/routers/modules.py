from fastapi import APIRouter
from ..models import ModuleRequest
from ..database import get_conn
from ..services.groq_agent import (
    analyze,
    SYSTEM_INVESTIGACION, SYSTEM_DIAGNOSTICO, SYSTEM_ESTRATEGIA,
    SYSTEM_PRODUCCION, SYSTEM_OPTIMIZACION, SYSTEM_SEGUIMIENTO,
)

router = APIRouter()


def _client_context(client_id) -> str:
    if not client_id:
        return ""
    conn = get_conn()
    row = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    conn.close()
    if not row:
        return ""
    c = dict(row)
    return f"""
PERFIL DEL CLIENTE:
- Nombre: {c['name']}
- Nicho: {c['niche'] or 'No especificado'}
- Descripción: {c['description'] or 'No especificada'}
- Instagram: {c['instagram'] or 'N/A'}
- TikTok: {c['tiktok'] or 'N/A'}
- Facebook: {c['facebook'] or 'N/A'}
- YouTube: {c['youtube'] or 'N/A'}
- Web: {c['website'] or 'N/A'}
- Tono de marca: {c['brand_tone'] or 'No definido'}
- Audiencia objetivo: {c['target_audience'] or 'No definida'}
"""


def _save(title: str, content: str, client_id, rtype: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO reports (type, title, content, client_id) VALUES (?, ?, ?, ?)",
        (rtype, title, content, client_id),
    )
    conn.commit()
    conn.close()


def _run(system: str, req: ModuleRequest, title: str, rtype: str):
    msg = f"{_client_context(req.client_id)}\n\n{req.context}"
    result = analyze(system, msg)
    _save(title, result, req.client_id, rtype)
    return {"result": result}


@router.post("/investigacion")
def investigacion(req: ModuleRequest):
    return _run(SYSTEM_INVESTIGACION, req, f"Investigación — {req.context[:60]}", "investigacion")


@router.post("/diagnostico")
def diagnostico(req: ModuleRequest):
    return _run(SYSTEM_DIAGNOSTICO, req, "Diagnóstico de presencia digital", "diagnostico")


@router.post("/estrategia")
def estrategia(req: ModuleRequest):
    return _run(SYSTEM_ESTRATEGIA, req, "Estrategia de marketing", "estrategia")


@router.post("/produccion")
def produccion(req: ModuleRequest):
    return _run(SYSTEM_PRODUCCION, req, "Producción de contenido", "produccion")


@router.post("/optimizacion")
def optimizacion(req: ModuleRequest):
    return _run(SYSTEM_OPTIMIZACION, req, "Optimización de rendimiento", "optimizacion")


@router.post("/seguimiento")
def seguimiento(req: ModuleRequest):
    return _run(SYSTEM_SEGUIMIENTO, req, "Seguimiento post-mentoría", "seguimiento")
