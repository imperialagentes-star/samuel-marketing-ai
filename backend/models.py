from pydantic import BaseModel
from typing import Optional


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
