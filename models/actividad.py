from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from config.db import Base


class Actividad(Base):
    __tablename__ = "actividades"

    id_actividad   = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo         = Column(String(200), nullable=False)
    descripcion    = Column(Text, nullable=True)
    archivo_url    = Column(String(500), nullable=True)   # guía subida por el docente
    nombre_archivo = Column(String(200), nullable=True)
    fecha_limite   = Column(Date, nullable=True)
    id_curso       = Column(Integer, ForeignKey("curso.id_curso", ondelete="CASCADE"), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())


class EntregaActividad(Base):
    __tablename__ = "entregas_actividad"

    id_entrega     = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_actividad   = Column(Integer, ForeignKey("actividades.id_actividad", ondelete="CASCADE"), nullable=False)
    id_estudiante  = Column(Integer, ForeignKey("estudiante.id_estudiante", ondelete="CASCADE"), nullable=False)
    archivo_url    = Column(String(500), nullable=False)
    nombre_archivo = Column(String(200), nullable=False)
    fecha_entrega  = Column(DateTime(timezone=True), server_default=func.now())
    comentario     = Column(Text, nullable=True)
    nota           = Column(Float, nullable=True)
