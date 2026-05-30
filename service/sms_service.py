"""
sms_service.py
Servicio de notificaciones por SMS y WhatsApp usando Twilio.
Envía mensajes al número de teléfono del usuario (SMS + WhatsApp)
cuando ocurren eventos importantes en el sistema.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def _formatear_numero(telefono: str) -> str:
    """
    Convierte un número colombiano al formato E.164 requerido por Twilio (+57XXXXXXXXXX).
    """
    numero = (
        telefono.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    if numero.startswith("+"):
        return numero
    if len(numero) == 10 and numero.startswith("3"):
        return f"+57{numero}"
    if len(numero) == 11 and numero.startswith("0"):
        return f"+57{numero[1:]}"
    if len(numero) == 12 and numero.startswith("57"):
        return f"+{numero}"
    return f"+{numero}"


class SMSService:
    def __init__(self):
        self.account_sid    = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token     = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number    = os.getenv("TWILIO_FROM")           # ej. +12015551234 (para SMS)
        self.whatsapp_from  = os.getenv(                         # ej. whatsapp:+14155238886
            "TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"
        )

    def _credenciales_ok(self) -> bool:
        return bool(self.account_sid and self.auth_token)

    def _get_client(self):
        from twilio.rest import Client
        return Client(self.account_sid, self.auth_token)

    # ─── Canales base ─────────────────────────────────────────────────────────

    def enviar_sms(self, to_number: str, mensaje: str) -> bool:
        """Envía un SMS usando el número de Twilio configurado."""
        if not self._credenciales_ok() or not self.from_number:
            print("[SMS] Credenciales o número Twilio no configurados — SMS omitido.")
            return False
        if not to_number or not to_number.strip():
            return False
        try:
            numero = _formatear_numero(to_number)
            msg = self._get_client().messages.create(
                body=mensaje,
                from_=self.from_number,
                to=numero,
            )
            print(f"[SMS] Enviado a {numero} — SID: {msg.sid}")
            return True
        except Exception as e:
            print(f"[SMS] Error al enviar a {to_number}: {e}")
            return False

    def enviar_whatsapp(self, to_number: str, mensaje: str) -> bool:
        """Envía un mensaje de WhatsApp usando el sandbox/número de Twilio."""
        if not self._credenciales_ok():
            print("[WhatsApp] Credenciales Twilio no configuradas — WhatsApp omitido.")
            return False
        if not to_number or not to_number.strip():
            return False
        try:
            numero = _formatear_numero(to_number)
            msg = self._get_client().messages.create(
                body=mensaje,
                from_=self.whatsapp_from,
                to=f"whatsapp:{numero}",
            )
            print(f"[WhatsApp] Enviado a {numero} — SID: {msg.sid}")
            return True
        except Exception as e:
            print(f"[WhatsApp] Error al enviar a {to_number}: {e}")
            return False

    def _notificar(self, to_number: Optional[str], mensaje: str) -> bool:
        """Envía por SMS y por WhatsApp en una sola llamada."""
        if not to_number:
            return False
        ok_sms = self.enviar_sms(to_number, mensaje)
        ok_wa  = self.enviar_whatsapp(to_number, mensaje)
        return ok_sms or ok_wa

    # ─── Templates de notificaciones ─────────────────────────────────────────

    def notify_user_created(self, to_number: Optional[str], nombre: str, rol: str, password: str) -> bool:
        """SMS + WhatsApp de bienvenida cuando se crea una cuenta nueva."""
        mensaje = (
            f"EduCampus: Hola {nombre}, tu cuenta de {rol} fue creada. "
            f"Clave temporal: {password}. "
            "Cambia tu contrasena al ingresar por primera vez."
        )
        return self._notificar(to_number, mensaje)

    def notify_grade_registered(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        tipo_evaluacion: str,
        nota: float,
    ) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"se registro tu nota de {tipo_evaluacion}: {nota}/5.0 "
            f"en el curso {curso}."
        )
        return self._notificar(to_number, mensaje)

    def notify_material_uploaded(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        nombre_archivo: str,
        docente: str,
    ) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"el docente {docente} subio nuevo material '{nombre_archivo}' "
            f"en el curso {curso}."
        )
        return self._notificar(to_number, mensaje)

    def notify_attendance_registered(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        fecha: str,
        presente: bool,
    ) -> bool:
        estado = "PRESENTE" if presente else "AUSENTE"
        aviso  = "" if presente else " Recuerda que las faltas afectan tu rendimiento."
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"tu asistencia del {fecha} en {curso} fue registrada como {estado}.{aviso}"
        )
        return self._notificar(to_number, mensaje)

    def notify_course_enrollment(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        docente: str,
    ) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"te inscribiste exitosamente al curso '{curso}' "
            f"con el docente {docente}."
        )
        return self._notificar(to_number, mensaje)

    def notify_profile_updated(self, to_number: Optional[str], nombre: str, rol: str) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre}, tu perfil de {rol} "
            "fue actualizado exitosamente. Si no realizaste este cambio, "
            "contacta al administrador."
        )
        return self._notificar(to_number, mensaje)

    def notify_account_deleted(self, to_number: Optional[str], nombre: str, rol: str) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre}, tu cuenta de {rol} "
            "ha sido eliminada del sistema. "
            "Contacta al administrador si tienes dudas."
        )
        return self._notificar(to_number, mensaje)

    def notify_grade_updated(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        tipo_evaluacion: str,
        nota_nueva: float,
    ) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"tu nota de {tipo_evaluacion} en {curso} fue actualizada a {nota_nueva}/5.0."
        )
        return self._notificar(to_number, mensaje)

    def notify_attendance_corrected(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        fecha: str,
        presente: bool,
    ) -> bool:
        estado = "PRESENTE" if presente else "AUSENTE"
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"tu asistencia del {fecha} en {curso} fue corregida a {estado}."
        )
        return self._notificar(to_number, mensaje)

    def notify_enrollment_cancelled(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
    ) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"tu inscripcion al curso '{curso}' ha sido cancelada. "
            "Contacta al administrador si tienes dudas."
        )
        return self._notificar(to_number, mensaje)

    def notify_course_updated(
        self,
        to_number: Optional[str],
        nombre: str,
        curso: str,
    ) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre}, "
            f"el curso '{curso}' ha sido actualizado. "
            "Ingresa al sistema para ver los cambios."
        )
        return self._notificar(to_number, mensaje)

    def notify_course_deleted(
        self,
        to_number: Optional[str],
        nombre: str,
        curso: str,
    ) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre}, "
            f"el curso '{curso}' ha sido eliminado del sistema. "
            "Contacta al administrador si tienes dudas."
        )
        return self._notificar(to_number, mensaje)

    def notify_material_deleted(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        nombre_archivo: str,
    ) -> bool:
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"el archivo '{nombre_archivo}' del curso '{curso}' fue eliminado."
        )
        return self._notificar(to_number, mensaje)


# Instancia global del servicio
sms_service = SMSService()
