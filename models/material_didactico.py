from sqlalchemy import Column, Integer, String, Date, ForeignKey
from config.db import Base

class MaterialDidactico(Base):
    __tablename__ = "material_didactico"

    id_material = Column(Integer, primary_key=True)
    id_curso = Column(Integer, ForeignKey("curso.id_curso", ondelete="CASCADE"))
    archivo_url = Column(String(255), nullable=False)
    nombre_archivo = Column(String(120), nullable=False)
    fecha = Column(Date, nullable=False)
