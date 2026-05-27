"""
routers/notificaciones.py
Endpoints para gestión de notificaciones en la plataforma.

Cubre lectura, marcado y eliminación de notificaciones para
los tres roles: administrador, docente y estudiante.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from config.db import SessionLocal
from models.notificacion import Notificacion
from schemas.notificacion import NotificacionCreate, NotificacionResponse


router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{tipo_destinatario}/{id_destinatario}", response_model=List[NotificacionResponse])
def listar_notificaciones(tipo_destinatario: str, id_destinatario: int,
                          db: Session = Depends(get_db)):
    """Retorna todas las notificaciones de un usuario, ordenadas por fecha descendente."""
    return (
        db.query(Notificacion)
        .filter(
            Notificacion.tipo_destinatario == tipo_destinatario,
            Notificacion.id_destinatario  == id_destinatario,
        )
        .order_by(Notificacion.fecha_creacion.desc())
        .all()
    )


@router.get("/{tipo_destinatario}/{id_destinatario}/no-leidas")
def contar_no_leidas(tipo_destinatario: str, id_destinatario: int,
                     db: Session = Depends(get_db)):
    """Retorna el conteo de notificaciones no leídas (usado para el badge del sidebar)."""
    count = (
        db.query(Notificacion)
        .filter(
            Notificacion.tipo_destinatario == tipo_destinatario,
            Notificacion.id_destinatario  == id_destinatario,
            Notificacion.leida == False,
        )
        .count()
    )
    return {"no_leidas": count}


@router.put("/{id_notificacion}/leer", response_model=NotificacionResponse)
def marcar_leida(id_notificacion: int, db: Session = Depends(get_db)):
    """Marca una notificación específica como leída."""
    notificacion = db.query(Notificacion).filter(
        Notificacion.id_notificacion == id_notificacion
    ).first()
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notificacion.leida = True
    db.commit()
    db.refresh(notificacion)
    return notificacion


@router.put("/{tipo_destinatario}/{id_destinatario}/leer-todas")
def marcar_todas_leidas(tipo_destinatario: str, id_destinatario: int,
                        db: Session = Depends(get_db)):
    """Marca todas las notificaciones de un usuario como leídas de una vez."""
    db.query(Notificacion).filter(
        Notificacion.tipo_destinatario == tipo_destinatario,
        Notificacion.id_destinatario  == id_destinatario,
        Notificacion.leida == False,
    ).update({"leida": True})
    db.commit()
    return {"ok": True}


@router.delete("/{id_notificacion}")
def eliminar_notificacion(id_notificacion: int, db: Session = Depends(get_db)):
    """Elimina permanentemente una notificación."""
    notificacion = db.query(Notificacion).filter(
        Notificacion.id_notificacion == id_notificacion
    ).first()
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db.delete(notificacion)
    db.commit()
    return {"ok": True}


@router.post("/", response_model=NotificacionResponse)
def crear_notificacion_manual(data: NotificacionCreate, db: Session = Depends(get_db)):
    """Crea una notificación de forma manual (uso administrativo)."""
    notificacion = Notificacion(**data.model_dump())
    db.add(notificacion)
    db.commit()
    db.refresh(notificacion)
    return notificacion
