"""
email_service.py
Servicio de notificaciones por correo usando Gmail SMTP.
Envía emails HTML a los usuarios cuando ocurren eventos
importantes en el sistema EduCampus.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    def __init__(self):
        self.gmail_user = os.getenv("GMAIL_USER")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        self.from_email = os.getenv("EMAIL_FROM", self.gmail_user)

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
        """Envía un email usando Gmail SMTP SSL (puerto 465) con fallback a TLS (587)."""
        if not self.gmail_user or not self.gmail_password:
            print("[Email] GMAIL_USER o GMAIL_APP_PASSWORD no configurados — email omitido.")
            return None

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"EduCampus <{self.from_email}>"
            msg["To"] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            # Intento 1: SMTP_SSL puerto 465 (más confiable en servidores cloud)
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
                    server.login(self.gmail_user, self.gmail_password)
                    server.sendmail(self.from_email, to_email, msg.as_string())
                print(f"[Email] Enviado (SSL/465) a {to_email} — {subject}")
                return True
            except Exception as e_ssl:
                print(f"[Email] SSL/465 falló ({e_ssl}), intentando TLS/587...")
                # Intento 2: STARTTLS puerto 587
                with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
                    server.ehlo()
                    server.starttls()
                    server.login(self.gmail_user, self.gmail_password)
                    server.sendmail(self.from_email, to_email, msg.as_string())
                print(f"[Email] Enviado (TLS/587) a {to_email} — {subject}")
                return True

        except smtplib.SMTPAuthenticationError:
            print("[Email] Error de autenticacion: verifica GMAIL_USER y GMAIL_APP_PASSWORD en las variables de entorno.")
            return None
        except Exception as e:
            print(f"[Email] Error al enviar a {to_email}: {e}")
            return None

    # ─── Templates de notificaciones ─────────────────────────────────────────

    def notify_user_created(self, to_email: str, nombre: str, rol: str, password: str):
        """Notifica a un usuario que su cuenta ha sido creada."""
        subject = "Bienvenido al EduCampus"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #2e86de; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">Sistema Académico EduCampus</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #2e86de;">¡Bienvenido, {nombre}!</h2>
                    <p>Tu cuenta de <strong>{rol}</strong> ha sido creada exitosamente.</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #2e86de; margin: 20px 0;">
                        <p><strong>Correo:</strong> {to_email}</p>
                        <p><strong>Contraseña temporal:</strong> {password}</p>
                    </div>
                    <p style="color: #e74c3c;"><strong>⚠️ Importante:</strong> Por seguridad, te recomendamos cambiar tu contraseña al iniciar sesión por primera vez.</p>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                    <p>&copy; 2025 Sistema Académico EduCampus</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_grade_registered(self, to_email: str, nombre_estudiante: str, curso: str, tipo_evaluacion: str, nota: float):
        """Notifica a un estudiante que se registró una calificación."""
        subject = f"Nueva Calificación Registrada - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #27ae60; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">📊 Nueva Calificación</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #27ae60;">Hola {nombre_estudiante},</h2>
                    <p>Se ha registrado una nueva calificación en tu curso.</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #27ae60; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                        <p><strong>Tipo de Evaluación:</strong> {tipo_evaluacion}</p>
                        <p><strong>Nota:</strong> <span style="font-size: 24px; color: #27ae60; font-weight: bold;">{nota}/5.0</span></p>
                    </div>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_material_uploaded(self, to_email: str, nombre_estudiante: str, curso: str, nombre_archivo: str, docente: str):
        """Notifica a un estudiante que se subió nuevo material didáctico."""
        subject = f"Nuevo Material Didáctico - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f39c12; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">📚 Nuevo Material Disponible</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #f39c12;">Hola {nombre_estudiante},</h2>
                    <p>El docente <strong>{docente}</strong> ha subido nuevo material didáctico.</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #f39c12; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                        <p><strong>Archivo:</strong> {nombre_archivo}</p>
                    </div>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_attendance_registered(self, to_email: str, nombre_estudiante: str, curso: str, fecha: str, presente: bool):
        """Notifica a un estudiante sobre el registro de asistencia."""
        estado = "Presente ✅" if presente else "Ausente ❌"
        color = "#27ae60" if presente else "#e74c3c"
        subject = f"Registro de Asistencia - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: {color}; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">📋 Registro de Asistencia</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: {color};">Hola {nombre_estudiante},</h2>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid {color}; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                        <p><strong>Fecha:</strong> {fecha}</p>
                        <p><strong>Estado:</strong> {estado}</p>
                    </div>
                    {"<p style='color: #e74c3c;'>⚠️ Recuerda que las faltas pueden afectar tu rendimiento académico.</p>" if not presente else ""}
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_course_enrollment(self, to_email: str, nombre_estudiante: str, curso: str, docente: str):
        """Notifica a un estudiante sobre su inscripción a un curso."""
        subject = f"Inscripción Exitosa - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #9b59b6; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">🎓 Inscripción Exitosa</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #9b59b6;">¡Felicidades {nombre_estudiante}!</h2>
                    <p>Te has inscrito exitosamente al siguiente curso:</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #9b59b6; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                        <p><strong>Docente:</strong> {docente}</p>
                    </div>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_profile_updated(self, to_email: str, nombre: str, rol: str):
        """Notifica a un usuario que su perfil fue actualizado."""
        subject = "Tu perfil ha sido actualizado - EduCampus"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #2e86de; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">✏️ Perfil Actualizado</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #2e86de;">Hola {nombre},</h2>
                    <p>Tu perfil de <strong>{rol}</strong> en EduCampus ha sido actualizado exitosamente.</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #2e86de; margin: 20px 0;">
                        <p>Si no realizaste o solicitaste este cambio, comunícate de inmediato con el administrador del sistema.</p>
                    </div>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                    <p>&copy; 2025 Sistema Académico EduCampus</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_account_deleted(self, to_email: str, nombre: str, rol: str):
        """Notifica a un usuario que su cuenta fue eliminada."""
        subject = "Cuenta eliminada - EduCampus"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #e74c3c; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">🗑️ Cuenta Eliminada</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #e74c3c;">Hola {nombre},</h2>
                    <p>Tu cuenta de <strong>{rol}</strong> ha sido eliminada del sistema EduCampus.</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #e74c3c; margin: 20px 0;">
                        <p>Si tienes alguna duda sobre esta acción, contacta al administrador.</p>
                    </div>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                    <p>&copy; 2025 Sistema Académico EduCampus</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_grade_updated(self, to_email: str, nombre_estudiante: str, curso: str, tipo_evaluacion: str, nota_nueva: float):
        """Notifica a un estudiante que su calificación fue actualizada."""
        subject = f"Calificación Actualizada - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #27ae60; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">📊 Calificación Actualizada</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #27ae60;">Hola {nombre_estudiante},</h2>
                    <p>Tu calificación ha sido actualizada.</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #27ae60; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                        <p><strong>Tipo de Evaluación:</strong> {tipo_evaluacion}</p>
                        <p><strong>Nueva Nota:</strong> <span style="font-size: 24px; color: #27ae60; font-weight: bold;">{nota_nueva}/5.0</span></p>
                    </div>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_attendance_corrected(self, to_email: str, nombre_estudiante: str, curso: str, fecha: str, presente: bool):
        """Notifica a un estudiante que su asistencia fue corregida."""
        estado = "Presente ✅" if presente else "Ausente ❌"
        color = "#27ae60" if presente else "#e74c3c"
        subject = f"Asistencia Corregida - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: {color}; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">📋 Asistencia Corregida</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: {color};">Hola {nombre_estudiante},</h2>
                    <p>Tu registro de asistencia ha sido corregido.</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid {color}; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                        <p><strong>Fecha:</strong> {fecha}</p>
                        <p><strong>Estado corregido:</strong> {estado}</p>
                    </div>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_enrollment_cancelled(self, to_email: str, nombre_estudiante: str, curso: str):
        """Notifica a un estudiante que su inscripción fue cancelada."""
        subject = f"Inscripción Cancelada - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #e74c3c; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">❌ Inscripción Cancelada</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #e74c3c;">Hola {nombre_estudiante},</h2>
                    <p>Tu inscripción al siguiente curso ha sido cancelada:</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #e74c3c; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                    </div>
                    <p>Si tienes preguntas, contacta al administrador.</p>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_course_updated(self, to_email: str, nombre: str, curso: str):
        """Notifica a un usuario que un curso fue actualizado."""
        subject = f"Curso Actualizado - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f39c12; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">📚 Curso Actualizado</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #f39c12;">Hola {nombre},</h2>
                    <p>El siguiente curso ha sido actualizado:</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #f39c12; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                    </div>
                    <p>Ingresa al sistema para ver los cambios actualizados.</p>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_course_deleted(self, to_email: str, nombre: str, curso: str):
        """Notifica a un usuario que un curso fue eliminado."""
        subject = f"Curso Eliminado - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #e74c3c; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">🗑️ Curso Eliminado</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #e74c3c;">Hola {nombre},</h2>
                    <p>El siguiente curso ha sido eliminado del sistema:</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #e74c3c; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                    </div>
                    <p>Si tienes preguntas, contacta al administrador.</p>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

    def notify_material_deleted(self, to_email: str, nombre_estudiante: str, curso: str, nombre_archivo: str):
        """Notifica a un estudiante que un material fue eliminado."""
        subject = f"Material Eliminado - {curso}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #95a5a6; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">📁 Material Eliminado</h1>
                </div>
                <div style="padding: 30px; background-color: #f5f5f5;">
                    <h2 style="color: #7f8c8d;">Hola {nombre_estudiante},</h2>
                    <p>El siguiente material ha sido eliminado del curso:</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid #95a5a6; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                        <p><strong>Archivo:</strong> {nombre_archivo}</p>
                    </div>
                </div>
                <div style="padding: 20px; text-align: center; color: #888; font-size: 12px;">
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)


# Instancia global del servicio
email_service = EmailService()
