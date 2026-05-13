from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.docente import Docente
from models.estudiante import Estudiante
from models.administrador import Administrador
from pydantic import BaseModel
from utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginRequest(BaseModel):
    correo: str
    contraseña: str

class LoginResponse(BaseModel):
    id: int
    nombres: str | None = None
    apellidos: str | None = None
    nombre: str | None = None
    correo: str
    rol: str
    especialidad: str | None = None
    telefono: str | None = None
    estado: bool | None = None

@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # Buscar administrador
    administrador = db.query(Administrador).filter(
        Administrador.correo == credentials.correo
    ).first()
    
    if administrador and verify_password(credentials.contraseña, administrador.contraseña):
        return LoginResponse(
            id=administrador.id_administrador,
            nombre=administrador.nombre,
            correo=administrador.correo,
            rol="admin"
        )
    
    # Buscar docente
    docente = db.query(Docente).filter(
        Docente.correo == credentials.correo
    ).first()
    
    if docente and verify_password(credentials.contraseña, docente.contraseña):
        return LoginResponse(
            id=docente.id_docente,
            nombres=docente.nombres,
            apellidos=docente.apellidos,
            correo=docente.correo,
            rol="docente",
            especialidad=docente.especialidad,
            estado=docente.estado
        )
    
    # Buscar estudiante
    estudiante = db.query(Estudiante).filter(
        Estudiante.correo == credentials.correo
    ).first()
    
    if estudiante and verify_password(credentials.contraseña, estudiante.contraseña):
        return LoginResponse(
            id=estudiante.id_estudiante,
            nombres=estudiante.nombres,
            apellidos=estudiante.apellidos,
            correo=estudiante.correo,
            rol="estudiante",
            telefono=estudiante.telefono,
            estado=estudiante.estado
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas"
    )
