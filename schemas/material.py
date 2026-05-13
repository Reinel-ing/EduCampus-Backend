from pydantic import BaseModel, ConfigDict
from datetime import date

class MaterialBase(BaseModel):
    id_curso: int
    archivo_url: str
    nombre_archivo: str
    fecha: date

class MaterialCreate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    id_material: int
    model_config = ConfigDict(from_attributes=True)
