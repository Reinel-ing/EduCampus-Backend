from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.docente import Docente
from models.curso import Curso
from models.estudiante import Estudiante
from models.estudiante_curso import EstudianteCurso
from models.calificacion import Calificacion
from schemas.docente import DocenteCreate, DocenteUpdate, DocenteResponse
from utils.security import hash_password
from service.email_service import email_service

router = APIRouter(prefix="/docentes", tags=["Docentes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED)
def create_docente(docente: DocenteCreate, db: Session = Depends(get_db)):
    docente_data = docente.model_dump()
    plain_password = docente_data["contraseña"]
    
    # Hashear la contraseña
    docente_data["contraseña"] = hash_password(plain_password)
    
    db_docente = Docente(**docente_data)
    db.add(db_docente)
    db.commit()
    db.refresh(db_docente)
    
    # Enviar email de bienvenida
    try:
        email_service.notify_user_created(
            to_email=db_docente.correo,
            nombre=f"{db_docente.nombres} {db_docente.apellidos}",
            rol="Docente",
            password=plain_password
        )
    except Exception as e:
        print(f"Error al enviar email: {e}")
    
    return db_docente

@router.get("/", response_model=list[DocenteResponse])
def list_docentes(db: Session = Depends(get_db)):
    return db.query(Docente).all()

@router.get("/{docente_id}", response_model=DocenteResponse)
def get_docente(docente_id: int, db: Session = Depends(get_db)):
    docente = db.query(Docente).filter(Docente.id_docente == docente_id).first()
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    return docente

@router.put("/{docente_id}", response_model=DocenteResponse)
def update_docente(docente_id: int, docente: DocenteUpdate, db: Session = Depends(get_db)):
    db_docente = db.query(Docente).filter(Docente.id_docente == docente_id).first()
    if not db_docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    update_data = docente.model_dump(exclude_unset=True)
    
    # Si se actualiza la contraseña, hashearla
    if "contraseña" in update_data and update_data["contraseña"]:
        update_data["contraseña"] = hash_password(update_data["contraseña"])
    
    for key, value in update_data.items():
        setattr(db_docente, key, value)
    db.commit()
    db.refresh(db_docente)
    return db_docente

@router.delete("/{docente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_docente(docente_id: int, db: Session = Depends(get_db)):
    db_docente = db.query(Docente).filter(Docente.id_docente == docente_id).first()
    if not db_docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    db.delete(db_docente)
    db.commit()

@router.get("/{docente_id}/estudiantes-calificaciones", response_model=list[dict])
def estudiantes_calificaciones_docente(docente_id: int, db: Session = Depends(get_db)):
    from models.asistencia import Asistencia
    
    cursos = db.query(Curso).filter(Curso.id_docente == docente_id).all()
    
    if not cursos:
        return []
    
    resultado = []
    for curso in cursos:
        inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_curso == curso.id_curso).all()
        
        for inscripcion in inscripciones:
            estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == inscripcion.id_estudiante).first()
            if not estudiante:
                continue
            
            calificaciones = db.query(Calificacion).filter(
                Calificacion.id_estudiante == inscripcion.id_estudiante,
                Calificacion.id_curso == curso.id_curso
            ).all()
            
            if calificaciones:
                parcial1 = next((float(c.nota) for c in calificaciones if c.tipo_evaluacion == 1), 0)
                parcial2 = next((float(c.nota) for c in calificaciones if c.tipo_evaluacion == 2), 0)
                final = next((float(c.nota) for c in calificaciones if c.tipo_evaluacion == 3), 0)
                
                promedio = round((parcial1 * 0.30) + (parcial2 * 0.30) + (final * 0.40), 2)
                calificaciones_list = [{"tipo_evaluacion": c.tipo_evaluacion, "nota": float(c.nota)} for c in calificaciones]
            else:
                promedio = 0
                calificaciones_list = []
            
            asistencias = db.query(Asistencia).filter(
                Asistencia.id_estudiante == inscripcion.id_estudiante,
                Asistencia.id_curso == curso.id_curso
            ).all()
            
            total_asistencias = len(asistencias)
            presentes = len([a for a in asistencias if a.estado])
            porcentaje_asistencia = round((presentes / total_asistencias * 100), 2) if total_asistencias > 0 else 0
            
            resultado.append({
                "id_estudiante": estudiante.id_estudiante,
                "nombre_completo": f"{estudiante.nombres} {estudiante.apellidos}",
                "curso": curso.nombre,
                "promedio": promedio,
                "calificaciones": calificaciones_list,
                "asistencia": {
                    "total_clases": total_asistencias,
                    "asistencias": presentes,
                    "porcentaje": porcentaje_asistencia
                }
            })
    
    return resultado
