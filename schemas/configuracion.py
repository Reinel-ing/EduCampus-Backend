from pydantic import BaseModel, ConfigDict

class ConfiguracionBase(BaseModel):
    nombre_institucion: str
    email_contacto: str
    ano_academico: str

class ConfiguracionUpdate(BaseModel):
    nombre_institucion: str | None = None
    email_contacto: str | None = None
    ano_academico: str | None = None

class ConfiguracionResponse(ConfiguracionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
