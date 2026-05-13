from pydantic import BaseModel, ConfigDict
from datetime import date

class AsistenciaBase(BaseModel):
    id_estudiante: int
    id_curso: int
    fecha: date
    estado: bool

class AsistenciaCreate(AsistenciaBase):
    pass

class AsistenciaUpdate(BaseModel):
    estado: bool | None = None

class AsistenciaResponse(AsistenciaBase):
    id_asistencia: int
    model_config = ConfigDict(from_attributes=True)
