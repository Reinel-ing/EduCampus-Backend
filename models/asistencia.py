from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey
from config.db import Base

class Asistencia(Base):
    __tablename__ = "asistencia"

    id_asistencia = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante", ondelete="CASCADE"))
    id_curso = Column(Integer, ForeignKey("curso.id_curso", ondelete="CASCADE"))
    fecha = Column(Date, nullable=False)
    estado = Column(Boolean, nullable=False)  # True = asistió
