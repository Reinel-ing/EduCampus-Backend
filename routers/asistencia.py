from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.asistencia import Asistencia
from models.estudiante import Estudiante
from models.curso import Curso
from schemas.asistencia import AsistenciaCreate, AsistenciaUpdate, AsistenciaResponse
from service.email_service import email_service

router = APIRouter(prefix="/asistencia", tags=["Asistencia"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AsistenciaResponse, status_code=status.HTTP_201_CREATED)
def registrar_asistencia(asistencia: AsistenciaCreate, db: Session = Depends(get_db)):
    existe = db.query(Asistencia).filter(Asistencia.id_estudiante == asistencia.id_estudiante, Asistencia.id_curso == asistencia.id_curso, Asistencia.fecha == asistencia.fecha).first()
    if existe:
        raise HTTPException(status_code=400, detail="Asistencia ya registrada para ese día")
    db_asistencia = Asistencia(**asistencia.model_dump())
    db.add(db_asistencia)
    db.commit()
    db.refresh(db_asistencia)
    
    # Notificar al estudiante
    estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == asistencia.id_estudiante).first()
    curso = db.query(Curso).filter(Curso.id_curso == asistencia.id_curso).first()
    
    if estudiante and curso:
        try:
            email_service.notify_attendance_registered(
                to_email=estudiante.correo,
                nombre_estudiante=f"{estudiante.nombres} {estudiante.apellidos}",
                curso=curso.nombre,
                fecha=str(asistencia.fecha),
                presente=asistencia.estado
            )
        except Exception as e:
            print(f"Error al enviar email: {e}")
    
    return db_asistencia

@router.put("/{asistencia_id}", response_model=AsistenciaResponse)
def editar_asistencia(asistencia_id: int, asistencia: AsistenciaUpdate, db: Session = Depends(get_db)):
    db_asistencia = db.query(Asistencia).filter(Asistencia.id_asistencia == asistencia_id).first()
    if not db_asistencia:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    for key, value in asistencia.model_dump(exclude_unset=True).items():
        setattr(db_asistencia, key, value)
    db.commit()
    db.refresh(db_asistencia)
    return db_asistencia

@router.get("/por-estudiante/{estudiante_id}", response_model=list[AsistenciaResponse])
def asistencia_por_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    return db.query(Asistencia).filter(Asistencia.id_estudiante == estudiante_id).all()

@router.get("/por-curso/{curso_id}", response_model=list[AsistenciaResponse])
def asistencia_por_curso(curso_id: int, db: Session = Depends(get_db)):
    return db.query(Asistencia).filter(Asistencia.id_curso == curso_id).all()

@router.get("/porcentaje-estudiante/{estudiante_id}/{curso_id}", response_model=dict)
def porcentaje_asistencia(estudiante_id: int, curso_id: int, db: Session = Depends(get_db)):
    total = db.query(Asistencia).filter(Asistencia.id_estudiante == estudiante_id, Asistencia.id_curso == curso_id).count()
    presentes = db.query(Asistencia).filter(Asistencia.id_estudiante == estudiante_id, Asistencia.id_curso == curso_id, Asistencia.estado == True).count()
    porcentaje = (presentes / total * 100) if total > 0 else 0
    return {"porcentaje": porcentaje}
