from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from config.db import Base

class EstudianteCurso(Base):
    __tablename__ = "estudiante_curso"

    id = Column(Integer, primary_key=True, index=True)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante", ondelete="CASCADE"))
    id_curso = Column(Integer, ForeignKey("curso.id_curso", ondelete="CASCADE"))
    fecha_inscripcion = Column(DateTime, default=datetime.utcnow)
