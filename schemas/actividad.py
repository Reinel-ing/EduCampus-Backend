from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class ActividadResponse(BaseModel):
    id_actividad: int
    titulo: str
    descripcion: Optional[str]
    archivo_url: Optional[str]
    nombre_archivo: Optional[str]
    fecha_limite: Optional[date]
    id_curso: int
    fecha_creacion: Optional[datetime]
    model_config = {"from_attributes": True}


class EntregaActividadResponse(BaseModel):
    id_entrega: int
    id_actividad: int
    id_estudiante: int
    archivo_url: str
    nombre_archivo: str
    fecha_entrega: Optional[datetime]
    comentario: Optional[str]
    nota: Optional[float] = None
    model_config = {"from_attributes": True}
