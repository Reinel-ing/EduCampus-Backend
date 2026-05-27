from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Any

class CursoBase(BaseModel):
    nombre: str
    cupo_estudiante: int
    horario: List[Any]
    id_docente: int
    estado: bool = True

    @field_validator("cupo_estudiante")
    @classmethod
    def validar_cupo(cls, v):
        if v < 1:
            raise ValueError("El cupo de estudiantes debe ser al menos 1")
        return v

    @field_validator("horario")
    @classmethod
    def validar_horario(cls, v):
        if not v or len(v) == 0:
            raise ValueError("El horario debe tener al menos un elemento")
        return v

class CursoCreate(CursoBase):
    pass

class CursoUpdate(BaseModel):
    nombre: str | None = None
    cupo_estudiante: int | None = None
    horario: List[Any] | None = None
    id_docente: int | None = None
    estado: bool | None = None

class CursoResponse(CursoBase):
    id_curso: int
    model_config = ConfigDict(from_attributes=True)
