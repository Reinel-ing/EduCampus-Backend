from sqlalchemy import Column, Integer, Numeric, ForeignKey
from config.db import Base

class Calificacion(Base):
    __tablename__ = "calificacion"

    id_calificacion = Column(Integer, primary_key=True)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante", ondelete="CASCADE"))
    id_curso = Column(Integer, ForeignKey("curso.id_curso", ondelete="CASCADE"))
    tipo_evaluacion = Column(Integer)  # 1, 2 o 3
    nota = Column(Numeric(2, 1))
