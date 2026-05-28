from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.estudiante_curso import EstudianteCurso
from models.curso import Curso
from models.estudiante import Estudiante
from models.docente import Docente
from schemas.inscripcion import InscripcionCreate, InscripcionResponse
from service.email_service import email_service
from service.sms_service import sms_service
from service.notificacion_service import crear_notificacion, notificar_admins

router = APIRouter(prefix="/inscripciones", tags=["Inscripciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=InscripcionResponse, status_code=status.HTTP_201_CREATED)
def inscribir_estudiante(inscripcion: InscripcionCreate, db: Session = Depends(get_db)):
    # 1. Validar que el curso existe
    curso = db.query(Curso).filter(Curso.id_curso == inscripcion.id_curso).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # 2. Validar que el curso está activo
    if not curso.estado:
        raise HTTPException(status_code=400, detail="El curso está inactivo y no se pueden hacer inscripciones")
    
    # 3. Validar que el curso tiene docente asignado
    if not curso.id_docente:
        raise HTTPException(status_code=400, detail="El curso no tiene docente asignado")
    
    # 4. Validar que el estudiante existe
    estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == inscripcion.id_estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # 5. Validar que el estudiante tiene correo
    if not estudiante.correo:
        raise HTTPException(status_code=400, detail="El estudiante no tiene correo registrado")
    
    # 6. Validar que el correo sea válido y de dominio permitido (Gmail u Outlook)
    correo_lower = estudiante.correo.lower()
    if "@" not in correo_lower or "." not in correo_lower:
        raise HTTPException(status_code=400, detail="El correo del estudiante no es válido")
    
    # Dominios permitidos: gmail, hotmail, outlook
    dominios_permitidos = ("@gmail.com", "@hotmail.com", "@outlook.com", "@hotmail.es", "@outlook.es")
    if not any(correo_lower.endswith(d) for d in dominios_permitidos):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten correos Gmail, Hotmail u Outlook"
        )
    
    # 7. Validar que el estudiante está activo
    if not estudiante.estado:
        raise HTTPException(status_code=400, detail="El estudiante está inactivo y no puede inscribirse")
    
    # 8. Validar que no esté duplicado
    repetido = db.query(EstudianteCurso).filter(
        EstudianteCurso.id_curso == inscripcion.id_curso,
        EstudianteCurso.id_estudiante == inscripcion.id_estudiante
    ).first()
    if repetido:
        raise HTTPException(status_code=400, detail="El estudiante ya está inscrito en este curso")
    
    # 9. Validar que hay cupo disponible
    inscritos = db.query(EstudianteCurso).filter(EstudianteCurso.id_curso == inscripcion.id_curso).count()
    if inscritos >= curso.cupo_estudiante:
        raise HTTPException(status_code=400, detail="El curso ha alcanzado su cupo máximo de estudiantes")
    
    # Crear la inscripción
    db_inscripcion = EstudianteCurso(**inscripcion.model_dump())
    db.add(db_inscripcion)
    db.commit()
    db.refresh(db_inscripcion)
    
    # Notificar al estudiante sobre la inscripción
    estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == inscripcion.id_estudiante).first()
    docente = db.query(Docente).filter(Docente.id_docente == curso.id_docente).first()
    
    if estudiante and docente:
        # Notificacion en BD para el estudiante
        crear_notificacion(
            db,
            titulo=f"Inscripcion exitosa - {curso.nombre}",
            mensaje=f"Te has inscrito exitosamente al curso '{curso.nombre}' con el docente {docente.nombres} {docente.apellidos}.",
            tipo="inscripcion",
            id_destinatario=estudiante.id_estudiante,
            tipo_destinatario="estudiante",
        )
        # Notificacion en BD para el docente
        crear_notificacion(
            db,
            titulo=f"Nuevo estudiante en {curso.nombre}",
            mensaje=f"{estudiante.nombres} {estudiante.apellidos} se ha inscrito en tu curso '{curso.nombre}'.",
            tipo="inscripcion",
            id_destinatario=docente.id_docente,
            tipo_destinatario="docente",
        )
        # Notificacion para los admins
        notificar_admins(
            db,
            titulo="Nueva matricula registrada",
            mensaje=f"{estudiante.nombres} {estudiante.apellidos} se matriculo en el curso '{curso.nombre}' (docente: {docente.nombres} {docente.apellidos}).",
            tipo="info",
        )
        db.commit()

        try:
            email_service.notify_course_enrollment(
                to_email=estudiante.correo,
                nombre_estudiante=f"{estudiante.nombres} {estudiante.apellidos}",
                curso=curso.nombre,
                docente=f"{docente.nombres} {docente.apellidos}"
            )
        except Exception as e:
            print(f"Error al enviar email: {e}")

        try:
            sms_service.notify_course_enrollment(
                to_number=estudiante.telefono,
                nombre_estudiante=f"{estudiante.nombres} {estudiante.apellidos}",
                curso=curso.nombre,
                docente=f"{docente.nombres} {docente.apellidos}"
            )
        except Exception as e:
            print(f"Error al enviar SMS: {e}")

    return db_inscripcion

@router.delete("/{inscripcion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_inscripcion(inscripcion_id: int, db: Session = Depends(get_db)):
    inscripcion = db.query(EstudianteCurso).filter(EstudianteCurso.id == inscripcion_id).first()
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    db.delete(inscripcion)
    db.commit()

@router.get("/por-estudiante/{estudiante_id}", response_model=list)
def cursos_por_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_estudiante == estudiante_id).all()
    return [i.id_curso for i in inscripciones]

@router.get("/por-curso/{curso_id}", response_model=list)
def estudiantes_por_curso(curso_id: int, db: Session = Depends(get_db)):
    inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_curso == curso_id).all()
    return [i.id_estudiante for i in inscripciones]

@router.get("/", response_model=list[InscripcionResponse])
def listar_inscripciones(db: Session = Depends(get_db)):
    """Lista todas las inscripciones del sistema"""
    return db.query(EstudianteCurso).all()

@router.get("/detalles/por-curso/{curso_id}")
def estudiantes_detalle_por_curso(curso_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle completo de estudiantes inscritos en un curso"""
    inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_curso == curso_id).all()
    estudiantes = []
    for insc in inscripciones:
        estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == insc.id_estudiante).first()
        if estudiante:
            estudiantes.append({
                "id_inscripcion": insc.id,
                "id_estudiante": estudiante.id_estudiante,
                "nombres": estudiante.nombres,
                "apellidos": estudiante.apellidos,
                "correo": estudiante.correo,
                "cedula": estudiante.cedula
            })
    return estudiantes
