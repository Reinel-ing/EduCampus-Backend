from pydantic import BaseModel, ConfigDict

class DocenteBase(BaseModel):
    nombres: str
    apellidos: str
    cedula: str
    correo: str
    especialidad: str | None = None
    estado: bool = True

class DocenteCreate(DocenteBase):
    contraseña: str

class DocenteUpdate(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    cedula: str | None = None
    correo: str | None = None
    contraseña: str | None = None
    especialidad: str | None = None
    estado: bool | None = None

class DocenteResponse(DocenteBase):
    id_docente: int
    model_config = ConfigDict(from_attributes=True)
