from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.administrador import Administrador
from schemas.administrador import AdministradorCreate, AdministradorUpdate, AdministradorResponse
from utils.security import hash_password
import re

router = APIRouter(prefix="/administrador", tags=["Administrador"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validar_contraseña(contraseña: str):
    """Valida que la contraseña cumpla con los requisitos de seguridad"""
    if len(contraseña) < 12:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 12 caracteres"
        )
    
    if not re.search(r'[A-Z]', contraseña):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos una letra mayúscula"
        )
    
    if not re.search(r'[a-z]', contraseña):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos una letra minúscula"
        )
    
    if not re.search(r'[0-9]', contraseña):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos un número"
        )
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contraseña):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos un carácter especial (!@#$%^&*...)"
        )

@router.post("/", response_model=AdministradorResponse, status_code=status.HTTP_201_CREATED)
def create_administrador(administrador: AdministradorCreate, db: Session = Depends(get_db)):
    admin_data = administrador.model_dump()
    
    # Validar contraseña antes de hashearla
    validar_contraseña(admin_data["contraseña"])
    
    admin_data["contraseña"] = hash_password(admin_data["contraseña"])
    
    db_administrador = Administrador(**admin_data)
    db.add(db_administrador)
    db.commit()
    db.refresh(db_administrador)
    return db_administrador

@router.get("/", response_model=list[AdministradorResponse])
def list_administradores(db: Session = Depends(get_db)):
    return db.query(Administrador).all()

@router.get("/{administrador_id}", response_model=AdministradorResponse)
def get_administrador(administrador_id: int, db: Session = Depends(get_db)):
    administrador = db.query(Administrador).filter(Administrador.id_administrador == administrador_id).first()
    if not administrador:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    return administrador

@router.put("/{administrador_id}", response_model=AdministradorResponse)
def update_administrador(administrador_id: int, administrador: AdministradorUpdate, db: Session = Depends(get_db)):
    db_administrador = db.query(Administrador).filter(Administrador.id_administrador == administrador_id).first()
    if not db_administrador:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    
    update_data = administrador.model_dump(exclude_unset=True)
    
    # Si se actualiza la contraseña, validarla y hashearla
    if "contraseña" in update_data and update_data["contraseña"]:
        validar_contraseña(update_data["contraseña"])
        update_data["contraseña"] = hash_password(update_data["contraseña"])
    
    for key, value in update_data.items():
        setattr(db_administrador, key, value)
    db.commit()
    db.refresh(db_administrador)
    return db_administrador

@router.delete("/{administrador_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_administrador(administrador_id: int, db: Session = Depends(get_db)):
    db_administrador = db.query(Administrador).filter(Administrador.id_administrador == administrador_id).first()
    if not db_administrador:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    db.delete(db_administrador)
    db.commit()
