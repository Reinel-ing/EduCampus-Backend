from pydantic import BaseModel, ConfigDict

class CalificacionBase(BaseModel):
    id_estudiante: int
    id_curso: int
    tipo_evaluacion: int
    nota: float

class CalificacionCreate(CalificacionBase):
    pass

class CalificacionUpdate(BaseModel):
    tipo_evaluacion: int | None = None
    nota: float | None = None

class CalificacionResponse(CalificacionBase):
    id_calificacion: int
    model_config = ConfigDict(from_attributes=True)
