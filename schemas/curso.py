from pydantic import BaseModel, ConfigDict
from typing import List, Any

class CursoBase(BaseModel):
    nombre: str
    cupo_estudiante: int
    horario: List[Any]
    id_docente: int
    estado: bool = True

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
