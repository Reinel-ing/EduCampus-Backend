"""
sms_service.py
Servicio de notificaciones por SMS usando Twilio.
Envía mensajes de texto al número de teléfono del usuario
cuando ocurren eventos importantes en el sistema.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def _formatear_numero(telefono: str) -> str:
    """
    Convierte un número colombiano al formato E.164 (+57XXXXXXXXXX).
    Si ya tiene código de país (+) lo deja igual.
    Elimina espacios, guiones y paréntesis.
    """
    numero = telefono.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if numero.startswith("+"):
        return numero
    # Número colombiano de 10 dígitos (ej. 3001234567)
    if len(numero) == 10 and numero.startswith("3"):
        return f"+57{numero}"
    # Número con 0 adelante (ej. 03001234567)
    if len(numero) == 11 and numero.startswith("0"):
        return f"+57{numero[1:]}"
    # Por si ya tiene 57 sin el +
    if len(numero) == 12 and numero.startswith("57"):
        return f"+{numero}"
    # Devolver tal como está con + si no coincide ningún patrón
    return f"+{numero}"


class SMSService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        self._client = None

    def _get_client(self):
        """Crea el cliente Twilio de forma diferida (lazy)."""
        if self._client is None:
            from twilio.rest import Client
            self._client = Client(self.account_sid, self.auth_token)
        return self._client

    def _credenciales_ok(self) -> bool:
        """Verifica que las credenciales estén configuradas."""
        return bool(
            self.account_sid
            and self.auth_token
            and self.from_number
            and not self.account_sid.startswith("ACxxx")
        )

    def enviar_sms(self, to_number: str, mensaje: str) -> bool:
        """
        Envía un SMS al número indicado.
        Devuelve True si tuvo éxito, False si no.
        Si las credenciales no están configuradas, muestra aviso y no falla.
        """
        if not self._credenciales_ok():
            print("[SMS] Credenciales Twilio no configuradas — SMS omitido.")
            return False

        if not to_number or not to_number.strip():
            return False

        try:
            numero_formateado = _formatear_numero(to_number)
            client = self._get_client()
            message = client.messages.create(
                body=mensaje,
                from_=self.from_number,
                to=numero_formateado,
            )
            print(f"[SMS] Enviado a {numero_formateado} — SID: {message.sid}")
            return True
        except Exception as e:
            print(f"[SMS] Error al enviar a {to_number}: {e}")
            return False

    # ─── Templates de notificaciones ─────────────────────────────────────────

    def notify_user_created(self, to_number: Optional[str], nombre: str, rol: str, password: str) -> bool:
        """SMS de bienvenida cuando se crea una cuenta nueva."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre}, tu cuenta de {rol} fue creada. "
            f"Correo: tu correo registrado | Clave temporal: {password}. "
            "Cambia tu contraseña al ingresar por primera vez."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_grade_registered(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        tipo_evaluacion: str,
        nota: float,
    ) -> bool:
        """SMS cuando se registra una calificación."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"se registro tu nota de {tipo_evaluacion}: {nota}/5.0 "
            f"en el curso {curso}. Ingresa al sistema para ver el detalle."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_material_uploaded(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        nombre_archivo: str,
        docente: str,
    ) -> bool:
        """SMS cuando el docente sube nuevo material didáctico."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"el docente {docente} subio nuevo material '{nombre_archivo}' "
            f"en el curso {curso}. Ingresa al sistema para descargarlo."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_attendance_registered(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        fecha: str,
        presente: bool,
    ) -> bool:
        """SMS cuando se registra la asistencia del estudiante."""
        if not to_number:
            return False
        estado = "PRESENTE" if presente else "AUSENTE"
        aviso = "" if presente else " Recuerda que las faltas afectan tu rendimiento."
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"tu asistencia del {fecha} en {curso} fue registrada como {estado}.{aviso}"
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_course_enrollment(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        docente: str,
    ) -> bool:
        """SMS cuando el estudiante es inscrito en un curso."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"te inscribiste exitosamente al curso '{curso}' "
            f"con el docente {docente}. Ingresa al sistema para ver el horario."
        )
        return self.enviar_sms(to_number, mensaje)


# Instancia global del servicio
sms_service = SMSService()
