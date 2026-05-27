"""
routers/actividades.py
Gestión de actividades académicas y entregas de estudiantes.

El flujo principal es:
  1. El docente crea una actividad (opcionalmente sube un archivo guía).
  2. Los estudiantes del curso reciben una notificación automática.
  3. Cada estudiante sube su entrega; el docente recibe notificación.
  4. El docente califica cada entrega; el estudiante recibe su nota.
"""

import os
from datetime import date
from typing import List, Optional

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models.actividad import Actividad, EntregaActividad
from models.curso import Curso
from models.docente import Docente
from models.estudiante import Estudiante
from models.estudiante_curso import EstudianteCurso
from schemas.actividad import ActividadResponse, EntregaActividadResponse
from service.notificacion_service import crear_notificacion, notificar_admins


load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

router = APIRouter(prefix="/actividades", tags=["Actividades"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _subir_archivo(file: UploadFile, carpeta: str, nombre: str) -> str:
    """Sube un archivo a Cloudinary y retorna la URL segura."""
    result = cloudinary.uploader.upload(
        file=file.file,
        resource_type="raw",
        public_id=f"{carpeta}/{nombre}_{file.filename}",
    )
    return result["secure_url"]


def _parsear_horario_item(h) -> tuple[str, str]:
    """Convierte un elemento de horario (dict o string) en (dia, hora)."""
    if isinstance(h, dict):
        return h.get("dia", ""), h.get("hora", "")
    if isinstance(h, str):
        partes = h.split(" ", 1)
        return partes[0], partes[1] if len(partes) > 1 else ""
    return "", ""


# -----------------------------------------------------------------------
# Actividades
# -----------------------------------------------------------------------

@router.post("/upload", response_model=ActividadResponse)
async def crear_actividad(
    titulo: str = Form(...),
    descripcion: str = Form(""),
    fecha_limite: Optional[str] = Form(None),
    id_curso: int = Form(...),
    archivo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """
    Crea una actividad para un curso.
    Si se adjunta un archivo, se sube a Cloudinary como guía descargable.
    Tras guardar, notifica automáticamente a todos los estudiantes inscritos.
    """
    archivo_url = nombre_archivo = None
    if archivo and archivo.filename:
        archivo_url    = _subir_archivo(archivo, "actividades", titulo)
        nombre_archivo = archivo.filename

    fecha = None
    if fecha_limite:
        try:
            fecha = date.fromisoformat(fecha_limite)
        except ValueError:
            pass

    nueva = Actividad(
        titulo=titulo,
        descripcion=descripcion,
        archivo_url=archivo_url,
        nombre_archivo=nombre_archivo,
        fecha_limite=fecha,
        id_curso=id_curso,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    # Notificar a los estudiantes del curso y al equipo administrativo
    try:
        curso = db.query(Curso).filter(Curso.id_curso == id_curso).first()
        nombre_curso = curso.nombre if curso else f"Curso {id_curso}"
        inscritos = db.query(EstudianteCurso).filter(
            EstudianteCurso.id_curso == id_curso
        ).all()
        for inscripcion in inscritos:
            crear_notificacion(
                db,
                titulo=f"Nueva actividad: {titulo}",
                mensaje=f"El docente publicó una nueva actividad en {nombre_curso}. Revisa la sección de actividades.",
                tipo="material",
                id_destinatario=inscripcion.id_estudiante,
                tipo_destinatario="estudiante",
            )
        notificar_admins(
            db,
            titulo="Nueva actividad publicada",
            mensaje=f"Se publicó la actividad '{titulo}' en {nombre_curso}.",
        )
        db.commit()
    except Exception as exc:
        print(f"[actividades] Error al notificar nueva actividad: {exc}")

    return nueva


@router.get("/por-curso/{curso_id}", response_model=List[ActividadResponse])
def actividades_por_curso(curso_id: int, db: Session = Depends(get_db)):
    """Lista las actividades publicadas en un curso específico."""
    return (
        db.query(Actividad)
        .filter(Actividad.id_curso == curso_id)
        .order_by(Actividad.fecha_creacion.desc())
        .all()
    )


@router.get("/por-docente/{docente_id}")
def actividades_por_docente(docente_id: int, db: Session = Depends(get_db)):
    """
    Lista todas las actividades publicadas por un docente,
    incluyendo el nombre del curso y el total de entregas recibidas.
    """
    cursos = db.query(Curso).filter(Curso.id_docente == docente_id).all()
    resultado = []

    for curso in cursos:
        actividades = (
            db.query(Actividad)
            .filter(Actividad.id_curso == curso.id_curso)
            .order_by(Actividad.fecha_creacion.desc())
            .all()
        )
        for act in actividades:
            total = db.query(EntregaActividad).filter(
                EntregaActividad.id_actividad == act.id_actividad
            ).count()
            resultado.append({
                "id_actividad":  act.id_actividad,
                "titulo":        act.titulo,
                "descripcion":   act.descripcion,
                "archivo_url":   act.archivo_url,
                "nombre_archivo":act.nombre_archivo,
                "fecha_limite":  str(act.fecha_limite) if act.fecha_limite else None,
                "id_curso":      act.id_curso,
                "nombre_curso":  curso.nombre,
                "fecha_creacion":act.fecha_creacion.isoformat() if act.fecha_creacion else None,
                "total_entregas":total,
            })

    return resultado


@router.get("/por-estudiante/{estudiante_id}")
def actividades_por_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """
    Lista las actividades disponibles para un estudiante según sus cursos inscritos.
    Incluye el estado de entrega y, si fue calificada, la nota obtenida.
    """
    inscritos = db.query(EstudianteCurso).filter(
        EstudianteCurso.id_estudiante == estudiante_id
    ).all()
    resultado = []

    for inscripcion in inscritos:
        curso = db.query(Curso).filter(Curso.id_curso == inscripcion.id_curso).first()
        if not curso:
            continue

        actividades = (
            db.query(Actividad)
            .filter(Actividad.id_curso == inscripcion.id_curso)
            .order_by(Actividad.fecha_creacion.desc())
            .all()
        )
        for act in actividades:
            entrega = db.query(EntregaActividad).filter(
                EntregaActividad.id_actividad == act.id_actividad,
                EntregaActividad.id_estudiante == estudiante_id,
            ).first()

            resultado.append({
                "id_actividad":  act.id_actividad,
                "titulo":        act.titulo,
                "descripcion":   act.descripcion,
                "archivo_url":   act.archivo_url,
                "nombre_archivo":act.nombre_archivo,
                "fecha_limite":  str(act.fecha_limite) if act.fecha_limite else None,
                "id_curso":      act.id_curso,
                "nombre_curso":  curso.nombre,
                "fecha_creacion":act.fecha_creacion.isoformat() if act.fecha_creacion else None,
                "entregado":     entrega is not None,
                "entrega": {
                    "id_entrega":    entrega.id_entrega,
                    "archivo_url":   entrega.archivo_url,
                    "nombre_archivo":entrega.nombre_archivo,
                    "fecha_entrega": entrega.fecha_entrega.isoformat() if entrega.fecha_entrega else None,
                    "comentario":    entrega.comentario,
                    "nota":          entrega.nota,
                } if entrega else None,
            })

    return resultado


# -----------------------------------------------------------------------
# Entregas
# -----------------------------------------------------------------------

@router.post("/{id_actividad}/entregas/upload", response_model=EntregaActividadResponse)
async def subir_entrega(
    id_actividad: int,
    id_estudiante: int = Form(...),
    comentario: str = Form(""),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Sube la entrega de un estudiante para una actividad.
    Si ya existía una entrega previa, la reemplaza (conservando la nota).
    Notifica al docente del curso y al equipo administrativo.
    """
    actividad = db.query(Actividad).filter(
        Actividad.id_actividad == id_actividad
    ).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    entrega_previa = db.query(EntregaActividad).filter(
        EntregaActividad.id_actividad == id_actividad,
        EntregaActividad.id_estudiante == id_estudiante,
    ).first()

    archivo_url = _subir_archivo(archivo, "entregas", f"{id_actividad}_{id_estudiante}")
    es_reemplazo = entrega_previa is not None

    if es_reemplazo:
        entrega_previa.archivo_url   = archivo_url
        entrega_previa.nombre_archivo = archivo.filename
        entrega_previa.comentario    = comentario
        db.commit()
        db.refresh(entrega_previa)
        entrega_guardada = entrega_previa
    else:
        nueva = EntregaActividad(
            id_actividad=id_actividad,
            id_estudiante=id_estudiante,
            archivo_url=archivo_url,
            nombre_archivo=archivo.filename,
            comentario=comentario,
        )
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        entrega_guardada = nueva

    # Notificar al docente del curso sobre la nueva entrega
    try:
        curso      = db.query(Curso).filter(Curso.id_curso == actividad.id_curso).first()
        estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == id_estudiante).first()
        nombre_est   = f"{estudiante.nombres} {estudiante.apellidos}" if estudiante else f"Estudiante {id_estudiante}"
        nombre_curso = curso.nombre if curso else f"Curso {actividad.id_curso}"
        accion       = "reemplazó su entrega" if es_reemplazo else "entregó la actividad"

        if curso and curso.id_docente:
            crear_notificacion(
                db,
                titulo=f"Nueva entrega: {actividad.titulo}",
                mensaje=f"{nombre_est} {accion} '{actividad.titulo}' en {nombre_curso}.",
                tipo="info",
                id_destinatario=curso.id_docente,
                tipo_destinatario="docente",
            )
        notificar_admins(
            db,
            titulo="Entrega de actividad recibida",
            mensaje=f"{nombre_est} entregó '{actividad.titulo}' en {nombre_curso}.",
        )
        db.commit()
    except Exception as exc:
        print(f"[actividades] Error al notificar entrega: {exc}")

    return entrega_guardada


@router.get("/{id_actividad}/entregas")
def listar_entregas(id_actividad: int, db: Session = Depends(get_db)):
    """Lista todas las entregas de una actividad con el nombre del estudiante y su nota."""
    entregas = db.query(EntregaActividad).filter(
        EntregaActividad.id_actividad == id_actividad
    ).all()

    resultado = []
    for entrega in entregas:
        est = db.query(Estudiante).filter(
            Estudiante.id_estudiante == entrega.id_estudiante
        ).first()
        resultado.append({
            "id_entrega":       entrega.id_entrega,
            "id_estudiante":    entrega.id_estudiante,
            "nombre_estudiante":f"{est.nombres} {est.apellidos}" if est else "Desconocido",
            "archivo_url":      entrega.archivo_url,
            "nombre_archivo":   entrega.nombre_archivo,
            "fecha_entrega":    entrega.fecha_entrega.isoformat() if entrega.fecha_entrega else None,
            "comentario":       entrega.comentario,
            "nota":             entrega.nota,
        })

    return resultado


@router.put("/entregas/{id_entrega}/calificar")
def calificar_entrega(
    id_entrega: int,
    nota: float = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    Asigna una nota (0.0 – 5.0) a la entrega de un estudiante.
    Al guardar, notifica al estudiante con su calificación.
    """
    if not (0.0 <= nota <= 5.0):
        raise HTTPException(status_code=400, detail="La nota debe estar entre 0.0 y 5.0")

    entrega = db.query(EntregaActividad).filter(
        EntregaActividad.id_entrega == id_entrega
    ).first()
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")

    entrega.nota = round(nota, 1)
    db.commit()
    db.refresh(entrega)

    # Notificar al estudiante sobre su calificación
    try:
        actividad = db.query(Actividad).filter(
            Actividad.id_actividad == entrega.id_actividad
        ).first()
        titulo_act = actividad.titulo if actividad else "Actividad"
        crear_notificacion(
            db,
            titulo=f"Actividad calificada: {titulo_act}",
            mensaje=f"Tu entrega de '{titulo_act}' fue calificada con {entrega.nota:.1f}/5.0.",
            tipo="calificacion",
            id_destinatario=entrega.id_estudiante,
            tipo_destinatario="estudiante",
        )
        db.commit()
    except Exception as exc:
        print(f"[actividades] Error al notificar calificación: {exc}")

    return {"ok": True, "nota": entrega.nota}


@router.delete("/{id_actividad}")
def eliminar_actividad(id_actividad: int, db: Session = Depends(get_db)):
    """Elimina una actividad y todas sus entregas asociadas (por cascade)."""
    actividad = db.query(Actividad).filter(
        Actividad.id_actividad == id_actividad
    ).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    db.delete(actividad)
    db.commit()
    return {"ok": True}
