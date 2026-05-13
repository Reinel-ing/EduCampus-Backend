from sqlalchemy import Column, Integer, String
from config.db import Base

class Configuracion(Base):
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True, default=1)
    nombre_institucion = Column(String(120), nullable=False)
    email_contacto = Column(String(120), nullable=False)
    ano_academico = Column(String(20), nullable=False)
