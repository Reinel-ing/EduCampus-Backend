from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificacionCreate(BaseModel):
    titulo: str
    mensaje: str
    tipo: str = "info"
    id_destinatario: int
    tipo_destinatario: str  # admin / docente / estudiante


class NotificacionResponse(BaseModel):
    id_notificacion: int
    titulo: str
    mensaje: str
    tipo: str
    leida: bool
    fecha_creacion: Optional[datetime]
    id_destinatario: int
    tipo_destinatario: str

    model_config = {"from_attributes": True}
