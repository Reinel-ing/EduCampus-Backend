from pydantic import BaseModel, ConfigDict, field_validator

class CalificacionBase(BaseModel):
    id_estudiante: int
    id_curso: int
    tipo_evaluacion: int
    nota: float

    @field_validator("nota")
    @classmethod
    def validar_nota(cls, v):
        if v < 0.0 or v > 5.0:
            raise ValueError("La nota debe estar entre 0.0 y 5.0 (escala colombiana)")
        return v

class CalificacionCreate(CalificacionBase):
    pass

class CalificacionUpdate(BaseModel):
    tipo_evaluacion: int | None = None
    nota: float | None = None

class CalificacionResponse(CalificacionBase):
    id_calificacion: int
    model_config = ConfigDict(from_attributes=True)
