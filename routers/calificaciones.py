from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.calificacion import Calificacion
from models.estudiante import Estudiante
from models.curso import Curso
from schemas.calificacion import CalificacionCreate, CalificacionUpdate, CalificacionResponse
from service.email_service import email_service

router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CalificacionResponse, status_code=status.HTTP_201_CREATED)
def crear_calificacion(calificacion: CalificacionCreate, db: Session = Depends(get_db)):
    if not (0 <= calificacion.nota <= 5):
        raise HTTPException(status_code=400, detail="Nota fuera de rango")
    db_calificacion = Calificacion(**calificacion.model_dump())
    db.add(db_calificacion)
    db.commit()
    db.refresh(db_calificacion)
    
    # Obtener datos del estudiante y curso para notificación
    estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == calificacion.id_estudiante).first()
    curso = db.query(Curso).filter(Curso.id_curso == calificacion.id_curso).first()
    
    if estudiante and curso:
        tipo_eval = {1: "Parcial 1", 2: "Parcial 2", 3: "Final"}.get(calificacion.tipo_evaluacion, "Evaluación")
        try:
            email_service.notify_grade_registered(
                to_email=estudiante.correo,
                nombre_estudiante=f"{estudiante.nombres} {estudiante.apellidos}",
                curso=curso.nombre,
                tipo_evaluacion=tipo_eval,
                nota=calificacion.nota
            )
        except Exception as e:
            print(f"Error al enviar email: {e}")
    
    return db_calificacion

@router.put("/{calificacion_id}", response_model=CalificacionResponse)
def actualizar_calificacion(calificacion_id: int, calificacion: CalificacionUpdate, db: Session = Depends(get_db)):
    db_calificacion = db.query(Calificacion).filter(Calificacion.id_calificacion == calificacion_id).first()
    if not db_calificacion:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    if calificacion.nota is not None and not (0 <= calificacion.nota <= 5):
        raise HTTPException(status_code=400, detail="Nota fuera de rango")
    for key, value in calificacion.model_dump(exclude_unset=True).items():
        setattr(db_calificacion, key, value)
    db.commit()
    db.refresh(db_calificacion)
    return db_calificacion

@router.get("/por-curso/{curso_id}", response_model=list[CalificacionResponse])
def calificaciones_por_curso(curso_id: int, db: Session = Depends(get_db)):
    return db.query(Calificacion).filter(Calificacion.id_curso == curso_id).all()

@router.get("/por-estudiante/{estudiante_id}", response_model=list[CalificacionResponse])
def calificaciones_por_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    return db.query(Calificacion).filter(Calificacion.id_estudiante == estudiante_id).all()

@router.get("/promedio-estudiante/{estudiante_id}", response_model=dict)
def promedio_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    calificaciones = db.query(Calificacion).filter(Calificacion.id_estudiante == estudiante_id).all()
    if not calificaciones:
        return {"promedio": None}
    promedio = sum([c.nota for c in calificaciones]) / len(calificaciones)
    return {"promedio": float(promedio)}

@router.get("/promedio-curso/{curso_id}", response_model=dict)
def promedio_curso(curso_id: int, db: Session = Depends(get_db)):
    calificaciones = db.query(Calificacion).filter(Calificacion.id_curso == curso_id).all()
    if not calificaciones:
        return {"promedio": None}
    promedio = sum([c.nota for c in calificaciones]) / len(calificaciones)
    return {"promedio": float(promedio)}
