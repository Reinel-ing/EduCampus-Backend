from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from config.db import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id_notificacion  = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo           = Column(String(200), nullable=False)
    mensaje          = Column(Text, nullable=False)
    tipo             = Column(String(50), default="info")   # bienvenida / calificacion / inscripcion / material / info
    leida            = Column(Boolean, default=False)
    fecha_creacion   = Column(DateTime(timezone=True), server_default=func.now())

    # A quién va dirigida
    id_destinatario    = Column(Integer, nullable=False)
    tipo_destinatario  = Column(String(20), nullable=False)  # admin / docente / estudiante
