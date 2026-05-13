from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.estudiante import Estudiante
from models.docente import Docente
from models.curso import Curso
from models.calificacion import Calificacion
from models.asistencia import Asistencia
from models.estudiante_curso import EstudianteCurso
from datetime import datetime, timedelta

router = APIRouter(prefix="/reportes", tags=["Reportes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/asistencia-general", response_model=dict)
def reporte_asistencia_general(db: Session = Depends(get_db)):
    total_estudiantes = db.query(Estudiante).filter(Estudiante.estado == True).count()
    total_cursos = db.query(Curso).filter(Curso.estado == True).count()
    total_registros = db.query(Asistencia).count()
    
    asistencias = db.query(Asistencia).all()
    total_asistencias = len(asistencias)
    presentes = len([a for a in asistencias if a.estado])
    porcentaje_asistencia = round((presentes / total_asistencias * 100), 2) if total_asistencias else 0
    
    return {
        "porcentaje_asistencia": porcentaje_asistencia,
        "total_estudiantes": total_estudiantes,
        "total_cursos": total_cursos,
        "total_registros": total_registros
    }

@router.get("/rendimiento-academico", response_model=dict)
def reporte_rendimiento_academico(db: Session = Depends(get_db)):
    calificaciones = db.query(Calificacion).all()
    
    if not calificaciones:
        return {
            "promedio_general": 0,
            "alto_rendimiento": 0,
            "requieren_apoyo": 0,
            "tasa_aprobacion": 0
        }
    
    promedio_general = round(sum([c.nota for c in calificaciones]) / len(calificaciones) * 20, 2)
    alto_rendimiento = len([c for c in calificaciones if c.nota >= 4.0])
    requieren_apoyo = len([c for c in calificaciones if c.nota < 3.0])
    aprobados = len([c for c in calificaciones if c.nota >= 3.0])
    tasa_aprobacion = round((aprobados / len(calificaciones) * 100), 2)
    
    return {
        "promedio_general": promedio_general,
        "alto_rendimiento": alto_rendimiento,
        "requieren_apoyo": requieren_apoyo,
        "tasa_aprobacion": tasa_aprobacion
    }

@router.get("/usuarios-activos", response_model=dict)
def reporte_usuarios_activos(db: Session = Depends(get_db)):
    fecha_mes_actual = datetime.now() - timedelta(days=30)
    
    total_estudiantes = db.query(Estudiante).filter(Estudiante.estado == True).count()
    total_docentes = db.query(Docente).filter(Docente.estado == True).count()
    
    nuevos_estudiantes = db.query(Estudiante).count()
    nuevos_docentes = db.query(Docente).count()
    nuevos_usuarios = nuevos_estudiantes + nuevos_docentes
    
    usuarios_activos = total_estudiantes + total_docentes
    
    return {
        "usuarios_activos": usuarios_activos,
        "total_estudiantes": total_estudiantes,
        "total_docentes": total_docentes,
        "nuevos_usuarios": nuevos_usuarios
    }

@router.get("/completo", response_model=dict)
def reporte_completo(db: Session = Depends(get_db)):
    asistencia = reporte_asistencia_general(db)
    rendimiento = reporte_rendimiento_academico(db)
    usuarios = reporte_usuarios_activos(db)
    
    return {
        "asistencia_general": asistencia,
        "rendimiento_academico": rendimiento,
        "usuarios_activos": usuarios
    }
