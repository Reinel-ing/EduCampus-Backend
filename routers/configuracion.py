from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.configuracion import Configuracion
from schemas.configuracion import ConfiguracionUpdate, ConfiguracionResponse, ConfiguracionBase

router = APIRouter(prefix="/configuracion", tags=["Configuración"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ConfiguracionResponse, status_code=status.HTTP_201_CREATED)
def crear_configuracion(configuracion: ConfiguracionBase, db: Session = Depends(get_db)):
    existe = db.query(Configuracion).filter(Configuracion.id == 1).first()
    if existe:
        raise HTTPException(status_code=400, detail="La configuración ya existe. Use el endpoint de actualización.")
    nueva_config = Configuracion(id=1, **configuracion.model_dump())
    db.add(nueva_config)
    db.commit()
    db.refresh(nueva_config)
    return nueva_config

@router.get("/", response_model=ConfiguracionResponse)
def obtener_configuracion(db: Session = Depends(get_db)):
    config = db.query(Configuracion).filter(Configuracion.id == 1).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config

@router.put("/", response_model=ConfiguracionResponse)
def actualizar_configuracion(configuracion: ConfiguracionUpdate, db: Session = Depends(get_db)):
    config = db.query(Configuracion).filter(Configuracion.id == 1).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    for key, value in configuracion.model_dump(exclude_unset=True).items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return config
