from pydantic import BaseModel, ConfigDict, field_validator

class AdministradorBase(BaseModel):
    nombre: str
    correo: str
    contraseña: str

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, v):
        correo = v.lower()
        if not (correo.endswith("@gmail.com") or correo.endswith("@outlook.com")):
            raise ValueError("Solo se permiten correos @gmail.com o @outlook.com")
        return correo

class AdministradorCreate(AdministradorBase):
    pass

class AdministradorUpdate(BaseModel):
    nombre: str | None = None
    correo: str | None = None
    contraseña: str | None = None

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, v):
        if v is not None:
            correo = v.lower()
            if not (correo.endswith("@gmail.com") or correo.endswith("@outlook.com")):
                raise ValueError("Solo se permiten correos @gmail.com o @outlook.com")
            return correo
        return v

class AdministradorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_administrador: int
    nombre: str
    correo: str
