from pydantic import BaseModel
from typing import Optional, List


class ClientCreate(BaseModel):
    name: str
    niche: Optional[str] = None
    description: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    website: Optional[str] = None
    brand_tone: Optional[str] = None
    target_audience: Optional[str] = None


class ClientUpdate(ClientCreate):
    active: Optional[int] = 1


class ModuleRequest(BaseModel):
    client_id: Optional[int] = None
    context: str
    extra: Optional[dict] = {}


class SettingsUpdate(BaseModel):
    report_hour: int = 8
    report_minute: int = 0
    monitor_keywords: str = "marketing digital,redes sociales,publicidad,ventas,contenido viral"


class WorkflowCreate(BaseModel):
    client_id: int
    name: str
    focus: Optional[str] = None
    event_type: Optional[str] = None        # conferencia|lanzamiento|campaña|apertura|colaboracion|otro
    event_description: Optional[str] = None
    event_date: Optional[str] = None        # YYYY-MM-DD
    timeline_type: str = "mensual"          # urgente|corto|mensual|continuo


class WorkflowContinue(BaseModel):
    samuel_notes: Optional[str] = None
    samuel_choice: str = "continue"         # continue|skip


class WorkflowRegenerate(BaseModel):
    samuel_notes: str
