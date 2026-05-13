from sqlalchemy import Column, Integer, String, Boolean
from config.db import Base

class Estudiante(Base):
    __tablename__ = "estudiante"

    id_estudiante = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    telefono = Column(String(20))
    estado = Column(Boolean, default=True)
