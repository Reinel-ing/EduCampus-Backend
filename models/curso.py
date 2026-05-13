from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from config.db import Base

class Curso(Base):
    __tablename__ = "curso"

    id_curso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    cupo_estudiante = Column(Integer, nullable=False)
    horario = Column(JSONB, nullable=False)
    id_docente = Column(Integer, ForeignKey("docente.id_docente"))
    estado = Column(Boolean, default=True)
