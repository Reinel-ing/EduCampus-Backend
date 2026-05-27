from pydantic import BaseModel, ConfigDict, field_validator

class EstudianteBase(BaseModel):
    nombres: str
    apellidos: str
    cedula: str
    correo: str
    telefono: str | None = None
    estado: bool = True

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, v):
        correo = v.lower()
        if not (correo.endswith("@gmail.com") or correo.endswith("@outlook.com")):
            raise ValueError("Solo se permiten correos @gmail.com o @outlook.com")
        return correo

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

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, v):
        if v is not None:
            correo = v.lower()
            if not (correo.endswith("@gmail.com") or correo.endswith("@outlook.com")):
                raise ValueError("Solo se permiten correos @gmail.com o @outlook.com")
            return correo
        return v

class EstudianteResponse(EstudianteBase):
    id_estudiante: int
    model_config = ConfigDict(from_attributes=True)
