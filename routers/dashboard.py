from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.estudiante import Estudiante
from models.docente import Docente
from models.curso import Curso
from models.calificacion import Calificacion
from models.asistencia import Asistencia
from models.material_didactico import MaterialDidactico
from models.estudiante_curso import EstudianteCurso

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/admin", response_model=dict)
def estadisticas_admin(db: Session = Depends(get_db)):
    total_estudiantes = db.query(Estudiante).count()
    total_docentes = db.query(Docente).count()
    total_cursos = db.query(Curso).count()
    cursos_activos = db.query(Curso).filter(Curso.estado == True).count()
    calificaciones = db.query(Calificacion).all()
    asistencias = db.query(Asistencia).all()
    promedio_rendimiento = float(sum([c.nota for c in calificaciones]) / len(calificaciones)) if calificaciones else 0
    total_asistencias = len(asistencias)
    presentes = len([a for a in asistencias if a.estado])
    porcentaje_asistencia = float(presentes / total_asistencias * 100) if total_asistencias else 0
    return {
        "total_estudiantes": total_estudiantes,
        "total_docentes": total_docentes,
        "total_cursos": total_cursos,
        "cursos_activos": cursos_activos,
        "promedio_rendimiento": promedio_rendimiento,
        "porcentaje_asistencia": porcentaje_asistencia
    }

@router.get("/docente/{docente_id}", response_model=dict)
def estadisticas_docente(docente_id: int, db: Session = Depends(get_db)):
    cursos = db.query(Curso).filter(Curso.id_docente == docente_id).all()
    total_cursos = len(cursos)
    total_estudiantes = sum([db.query(EstudianteCurso).filter(EstudianteCurso.id_curso == c.id_curso).count() for c in cursos])
    material_subido = sum([db.query(MaterialDidactico).filter(MaterialDidactico.id_curso == c.id_curso).count() for c in cursos])
    return {
        "mis_cursos": total_cursos,
        "total_estudiantes": total_estudiantes,
        "material_subido": material_subido
    }

@router.get("/estudiante/{estudiante_id}", response_model=dict)
def estadisticas_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_estudiante == estudiante_id).all()
    mis_cursos = len(inscripciones)
    calificaciones = db.query(Calificacion).filter(Calificacion.id_estudiante == estudiante_id).all()
    promedio = float(sum([c.nota for c in calificaciones]) / len(calificaciones)) if calificaciones else 0
    asistencias = db.query(Asistencia).filter(Asistencia.id_estudiante == estudiante_id).all()
    total_asistencias = len(asistencias)
    presentes = len([a for a in asistencias if a.estado])
    porcentaje_asistencia = float(presentes / total_asistencias * 100) if total_asistencias else 0
    return {
        "mis_cursos": mis_cursos,
        "mi_promedio": promedio,
        "mi_asistencia": porcentaje_asistencia
    }
