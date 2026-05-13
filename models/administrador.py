from sqlalchemy import Column, Integer, String, Boolean
from config.db import Base

class Administrador(Base):
    __tablename__ = "administrador"
    
    id_administrador = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False, index=True)
    contraseña = Column(String, nullable=False)
