from pydantic import BaseModel, ConfigDict

class EstudianteBase(BaseModel):
    nombres: str
    apellidos: str
    cedula: str
    correo: str
    telefono: str | None = None
    estado: bool = True

class EstudianteCreate(EstudianteBase):
    contraseña: str

class EstudianteUpdate(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    cedula: str | None = None
    correo: str | None = None
    contraseña: str | None = None
    telefono: str | None = None
    estado: bool | None = None

class EstudianteResponse(EstudianteBase):
    id_estudiante: int
    model_config = ConfigDict(from_attributes=True)
