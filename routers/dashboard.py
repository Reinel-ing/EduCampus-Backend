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

@router.get("/rendimiento", response_model=dict)
def rendimiento_academico(db: Session = Depends(get_db)):
    from collections import defaultdict

    estudiantes = db.query(Estudiante).filter(Estudiante.estado == True).all()
    cursos_todos = db.query(Curso).filter(Curso.estado == True).all()

    ranking_estudiantes = []
    for est in estudiantes:
        cals = db.query(Calificacion).filter(Calificacion.id_estudiante == est.id_estudiante).all()
        if not cals:
            continue
        promedio = float(sum(float(c.nota) for c in cals) / len(cals))
        asists = db.query(Asistencia).filter(Asistencia.id_estudiante == est.id_estudiante).all()
        presentes = sum(1 for a in asists if a.estado)
        pct_asist = round(presentes / len(asists) * 100) if asists else 0
        mejor_cal = max(cals, key=lambda c: float(c.nota))
        curso_obj = db.query(Curso).filter(Curso.id_curso == mejor_cal.id_curso).first()
        mejor_curso = curso_obj.nombre if curso_obj else ""
        nota_r = round(promedio, 1)
        estado = "Excelente" if nota_r >= 4.5 else "Bueno" if nota_r >= 3.5 else "Regular" if nota_r >= 3.0 else "Bajo"
        ranking_estudiantes.append({
            "nombre": f"{est.nombres} {est.apellidos}",
            "curso": mejor_curso,
            "nota": nota_r,
            "asistencia": pct_asist,
            "pct": pct_asist,
            "estado": estado,
        })
    ranking_estudiantes.sort(key=lambda x: x["nota"], reverse=True)

    ranking_cursos = []
    for curso in cursos_todos:
        cals = db.query(Calificacion).filter(Calificacion.id_curso == curso.id_curso).all()
        if not cals:
            continue
        promedio = float(sum(float(c.nota) for c in cals) / len(cals))
        alumnos = db.query(EstudianteCurso).filter(EstudianteCurso.id_curso == curso.id_curso).count()
        by_student = defaultdict(list)
        for c in cals:
            by_student[c.id_estudiante].append(float(c.nota))
        mejor_id = max(by_student, key=lambda sid: sum(by_student[sid]) / len(by_student[sid]))
        mejor_est = db.query(Estudiante).filter(Estudiante.id_estudiante == mejor_id).first()
        mejor_nombre = f"{mejor_est.nombres} {mejor_est.apellidos}" if mejor_est else ""
        docente = db.query(Docente).filter(Docente.id_docente == curso.id_docente).first()
        docente_nombre = f"{docente.nombres} {docente.apellidos}" if docente else ""
        ranking_cursos.append({
            "nombre": curso.nombre,
            "docente": docente_nombre,
            "promedio": round(promedio, 1),
            "alumnos": alumnos,
            "top": mejor_nombre,
        })
    ranking_cursos.sort(key=lambda x: x["promedio"], reverse=True)

    promedio_general = round(sum(e["nota"] for e in ranking_estudiantes) / len(ranking_estudiantes), 1) if ranking_estudiantes else 0

    return {
        "promedio_general": promedio_general,
        "estudiantes": ranking_estudiantes,
        "cursos": ranking_cursos,
    }
