from sqlalchemy import Column, Integer, String, Boolean
from config.db import Base

class Docente(Base):
    __tablename__ = "docente"

    id_docente = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    especialidad = Column(String(100))
    telefono = Column(String(20))
    estado = Column(Boolean, default=True)
