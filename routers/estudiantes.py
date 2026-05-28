from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.estudiante import Estudiante
from models.curso import Curso
from models.estudiante_curso import EstudianteCurso
from schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse
from datetime import datetime
from utils.security import hash_password
from service.email_service import email_service
from service.sms_service import sms_service
from service.notificacion_service import crear_notificacion, notificar_admins

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EstudianteResponse, status_code=status.HTTP_201_CREATED)
def create_estudiante(estudiante: EstudianteCreate, db: Session = Depends(get_db)):
    estudiante_data = estudiante.model_dump()
    plain_password = estudiante_data["contraseña"]
    
    # Hashear la contraseña
    estudiante_data["contraseña"] = hash_password(plain_password)
    
    db_estudiante = Estudiante(**estudiante_data)
    db.add(db_estudiante)
    db.commit()
    db.refresh(db_estudiante)
    
    # Notificacion para el estudiante
    crear_notificacion(
        db,
        titulo="Bienvenido a EduCampus",
        mensaje="Tu cuenta de Estudiante ha sido creada exitosamente. Ya puedes acceder al sistema.",
        tipo="bienvenida",
        id_destinatario=db_estudiante.id_estudiante,
        tipo_destinatario="estudiante",
    )
    # Notificacion para los admins
    notificar_admins(
        db,
        titulo="Nuevo estudiante registrado",
        mensaje=f"El estudiante {db_estudiante.nombres} {db_estudiante.apellidos} ({db_estudiante.correo}) fue creado en el sistema.",
        tipo="sistema",
    )
    db.commit()

    # Enviar email de bienvenida
    try:
        email_service.notify_user_created(
            to_email=db_estudiante.correo,
            nombre=f"{db_estudiante.nombres} {db_estudiante.apellidos}",
            rol="Estudiante",
            password=plain_password
        )
    except Exception as e:
        print(f"Error al enviar email: {e}")

    # Enviar SMS de bienvenida si el estudiante tiene teléfono registrado
    try:
        sms_service.notify_user_created(
            to_number=db_estudiante.telefono,
            nombre=f"{db_estudiante.nombres} {db_estudiante.apellidos}",
            rol="Estudiante",
            password=plain_password
        )
    except Exception as e:
        print(f"Error al enviar SMS: {e}")

    return db_estudiante

@router.get("/", response_model=list[EstudianteResponse])
def list_estudiantes(db: Session = Depends(get_db)):
    return db.query(Estudiante).all()

@router.get("/{estudiante_id}", response_model=EstudianteResponse)
def get_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@router.put("/{estudiante_id}", response_model=EstudianteResponse)
def update_estudiante(estudiante_id: int, estudiante: EstudianteUpdate, db: Session = Depends(get_db)):
    db_estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == estudiante_id).first()
    if not db_estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    update_data = estudiante.model_dump(exclude_unset=True)
    
    # Si se actualiza la contraseña, hashearla
    if "contraseña" in update_data and update_data["contraseña"]:
        update_data["contraseña"] = hash_password(update_data["contraseña"])
    
    for key, value in update_data.items():
        setattr(db_estudiante, key, value)
    db.commit()
    db.refresh(db_estudiante)
    return db_estudiante

@router.delete("/{estudiante_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    db_estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == estudiante_id).first()
    if not db_estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    db.delete(db_estudiante)
    db.commit()

@router.get("/proximas-clases/{estudiante_id}", response_model=list[dict])
def obtener_clases_hoy(estudiante_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_estudiante == estudiante_id).all()
    curso_ids = [i.id_curso for i in inscripciones]
    
    if not curso_ids:
        return []
    
    cursos = db.query(Curso).filter(Curso.id_curso.in_(curso_ids), Curso.estado == True).all()
    
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_actual = dias_semana[datetime.now().weekday()]
    
    clases_hoy = []
    for curso in cursos:
        if curso.horario:
            for horario in curso.horario:
                if horario.get("dia") == dia_actual:
                    clases_hoy.append({
                        "id_curso": curso.id_curso,
                        "nombre_curso": curso.nombre,
                        "dia": horario.get("dia"),
                        "hora": horario.get("hora"),
                        "id_docente": curso.id_docente
                    })
    
    return clases_hoy
