"""
sms_service.py
Servicio de notificaciones por SMS usando Vonage.
Envía mensajes de texto al número de teléfono del usuario
cuando ocurren eventos importantes en el sistema.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def _formatear_numero(telefono: str) -> str:
    """
    Convierte un número colombiano al formato requerido por Vonage (sin +).
    Vonage espera el número en formato E.164 pero sin el símbolo +.
    """
    numero = (
        telefono.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    # Quitar el + si ya lo tiene
    if numero.startswith("+"):
        return numero[1:]
    # Número colombiano de 10 dígitos (ej. 3001234567)
    if len(numero) == 10 and numero.startswith("3"):
        return f"57{numero}"
    # Número con 0 adelante (ej. 03001234567)
    if len(numero) == 11 and numero.startswith("0"):
        return f"57{numero[1:]}"
    # Ya tiene 57 sin el +
    if len(numero) == 12 and numero.startswith("57"):
        return numero
    return numero


class SMSService:
    def __init__(self):
        self.api_key = os.getenv("VONAGE_API_KEY")
        self.api_secret = os.getenv("VONAGE_API_SECRET")
        self.from_name = os.getenv("VONAGE_FROM", "EduCampus")
        self._sms = None

    def _get_sms(self):
        """Crea el cliente Vonage de forma diferida (lazy)."""
        if self._sms is None:
            import vonage
            client = vonage.Client(key=self.api_key, secret=self.api_secret)
            self._sms = vonage.Sms(client)
        return self._sms

    def _credenciales_ok(self) -> bool:
        """Verifica que las credenciales estén configuradas."""
        return bool(
            self.api_key
            and self.api_secret
            and not self.api_key.startswith("xxx")
        )

    def enviar_sms(self, to_number: str, mensaje: str) -> bool:
        """
        Envía un SMS al número indicado con Vonage.
        Devuelve True si tuvo éxito, False si no.
        """
        if not self._credenciales_ok():
            print("[SMS] Credenciales Vonage no configuradas — SMS omitido.")
            return False

        if not to_number or not to_number.strip():
            return False

        try:
            numero_formateado = _formatear_numero(to_number)
            sms = self._get_sms()
            response = sms.send_message({
                "from": self.from_name,
                "to": numero_formateado,
                "text": mensaje,
            })
            if response["messages"][0]["status"] == "0":
                print(f"[SMS] Enviado a {numero_formateado} — ID: {response['messages'][0].get('message-id', '')}")
                return True
            else:
                error = response["messages"][0].get("error-text", "Error desconocido")
                print(f"[SMS] Error al enviar a {numero_formateado}: {error}")
                return False
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
            f"Clave temporal: {password}. "
            "Cambia tu contrasena al ingresar por primera vez."
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
            f"en el curso {curso}."
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
            f"en el curso {curso}."
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
            f"con el docente {docente}."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_profile_updated(self, to_number: Optional[str], nombre: str, rol: str) -> bool:
        """SMS cuando el perfil de un usuario es actualizado."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre}, tu perfil de {rol} "
            "fue actualizado exitosamente. Si no realizaste este cambio, "
            "contacta al administrador."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_account_deleted(self, to_number: Optional[str], nombre: str, rol: str) -> bool:
        """SMS cuando la cuenta de un usuario es eliminada."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre}, tu cuenta de {rol} "
            "ha sido eliminada del sistema. "
            "Contacta al administrador si tienes dudas."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_grade_updated(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        tipo_evaluacion: str,
        nota_nueva: float,
    ) -> bool:
        """SMS cuando una calificación es actualizada."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"tu nota de {tipo_evaluacion} en {curso} fue actualizada a {nota_nueva}/5.0."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_attendance_corrected(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        fecha: str,
        presente: bool,
    ) -> bool:
        """SMS cuando una asistencia es corregida."""
        if not to_number:
            return False
        estado = "PRESENTE" if presente else "AUSENTE"
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"tu asistencia del {fecha} en {curso} fue corregida a {estado}."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_enrollment_cancelled(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
    ) -> bool:
        """SMS cuando la inscripción de un estudiante es cancelada."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"tu inscripcion al curso '{curso}' ha sido cancelada. "
            "Contacta al administrador si tienes dudas."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_course_updated(
        self,
        to_number: Optional[str],
        nombre: str,
        curso: str,
    ) -> bool:
        """SMS cuando un curso es actualizado."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre}, "
            f"el curso '{curso}' ha sido actualizado. "
            "Ingresa al sistema para ver los cambios."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_course_deleted(
        self,
        to_number: Optional[str],
        nombre: str,
        curso: str,
    ) -> bool:
        """SMS cuando un curso es eliminado."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre}, "
            f"el curso '{curso}' ha sido eliminado del sistema. "
            "Contacta al administrador si tienes dudas."
        )
        return self.enviar_sms(to_number, mensaje)

    def notify_material_deleted(
        self,
        to_number: Optional[str],
        nombre_estudiante: str,
        curso: str,
        nombre_archivo: str,
    ) -> bool:
        """SMS cuando un material didáctico es eliminado."""
        if not to_number:
            return False
        mensaje = (
            f"EduCampus: Hola {nombre_estudiante}, "
            f"el archivo '{nombre_archivo}' del curso '{curso}' fue eliminado."
        )
        return self.enviar_sms(to_number, mensaje)


# Instancia global del servicio
sms_service = SMSService()
