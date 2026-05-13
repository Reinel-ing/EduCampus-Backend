from pydantic import BaseModel, ConfigDict

class AdministradorBase(BaseModel):
    nombre: str
    correo: str
    contraseña: str

class AdministradorCreate(AdministradorBase):
    pass

class AdministradorUpdate(BaseModel):
    nombre: str | None = None
    correo: str | None = None
    contraseña: str | None = None

class AdministradorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_administrador: int
    nombre: str
    correo: str
