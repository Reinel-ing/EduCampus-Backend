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
from service.email_service import email_service
from service.sms_service import sms_service


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


@router.post("/test-servicios")
def test_servicios_externos(email: str, telefono: str = None):
    """
    Prueba email, SMS y WhatsApp en producción.
    Llamar desde /docs → POST /notificaciones/test-servicios
    Parámetros: email=correo@ejemplo.com  telefono=3001234567 (opcional)
    """
    resultado = {
        "configuracion": {
            "gmail_user":           email_service.gmail_user or "NO CONFIGURADO",
            "gmail_password_ok":    bool(email_service.gmail_password),
            "twilio_account_ok":    bool(sms_service.account_sid),
            "twilio_auth_ok":       bool(sms_service.auth_token),
            "twilio_from":          sms_service.from_number or "NO CONFIGURADO",
            "twilio_whatsapp_from": sms_service.whatsapp_from or "NO CONFIGURADO",
        },
        "email":    {"ok": False, "detalle": ""},
        "sms":      {"ok": False, "detalle": ""},
        "whatsapp": {"ok": False, "detalle": ""},
    }

    # ── Test email ──────────────────────────────────────────────────────────
    ok_email = email_service.send_email(
        to_email=email,
        subject="[EduCampus] Prueba de notificacion por email",
        html_content="""
        <html>
          <body style="font-family:Arial,sans-serif;max-width:500px;margin:0 auto;padding:20px;">
            <div style="background:#2e86de;padding:18px;text-align:center;">
              <h2 style="color:white;margin:0;">EduCampus — Prueba de Email</h2>
            </div>
            <div style="padding:24px;background:#f5f5f5;">
              <p>Este es un correo de prueba del sistema EduCampus.</p>
              <p>Si recibes este mensaje, el servicio de email funciona
                 correctamente en produccion.</p>
            </div>
          </body>
        </html>
        """
    )
    resultado["email"]["ok"]     = bool(ok_email)
    resultado["email"]["detalle"] = (
        "Enviado correctamente" if ok_email
        else "Fallo — revisa los logs de Render para ver el error exacto"
    )

    # ── Test SMS y WhatsApp ─────────────────────────────────────────────────
    if telefono:
        ok_sms = sms_service.enviar_sms(
            to_number=telefono,
            mensaje="EduCampus: Prueba de SMS. Si recibes esto, el servicio SMS funciona correctamente."
        )
        resultado["sms"]["ok"]     = bool(ok_sms)
        resultado["sms"]["detalle"] = (
            "Enviado correctamente" if ok_sms
            else "Fallo — revisa los logs de Render para ver el error exacto"
        )

        ok_wa = sms_service.enviar_whatsapp(
            to_number=telefono,
            mensaje="EduCampus: Prueba de WhatsApp. Si recibes esto, el servicio WhatsApp funciona correctamente."
        )
        resultado["whatsapp"]["ok"]     = bool(ok_wa)
        resultado["whatsapp"]["detalle"] = (
            "Enviado correctamente" if ok_wa
            else "Fallo — asegurate de haber enviado el codigo de union al sandbox de Twilio"
        )
    else:
        resultado["sms"]["detalle"]      = "No se envio — proporciona el parametro 'telefono' para probar"
        resultado["whatsapp"]["detalle"] = "No se envio — proporciona el parametro 'telefono' para probar"

    return resultado
