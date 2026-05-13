from pydantic import BaseModel, ConfigDict
from datetime import datetime

class InscripcionBase(BaseModel):
    id_estudiante: int
    id_curso: int
    fecha_inscripcion: datetime | None = None

class InscripcionCreate(BaseModel):
    id_estudiante: int
    id_curso: int

class InscripcionResponse(InscripcionBase):
    id: int
    fecha_inscripcion: datetime
    model_config = ConfigDict(from_attributes=True)
