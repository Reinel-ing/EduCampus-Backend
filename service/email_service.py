from mailersend import Email, MailerSendClient, EmailBuilder
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class EmailService:
    def __init__(self):
        self.api_key = os.getenv("MAILERSEND_API_KEY")
        self.from_email = os.getenv("EMAIL_FROM", "noreply@educampus.edu.co")
        self.client = MailerSendClient(self.api_key)

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
        """
        Envía un email usando MailerSend.
        """
        try:
            email = (EmailBuilder()
                .from_email(self.from_email, "EduCampus")
                .to_many([{"email": to_email, "name": to_email.split("@")[0]}])
                .subject(subject)
                .html(html_content)
                .text(text_content or "")
                .build()
            )
            response = self.client.emails.send(email)
            print(f"Email sent: {getattr(response, 'message_id', response)}")
            return response
        except Exception as e:
            print(f"Error al enviar email: {str(e)}")
            return None
    
    # Templates de notificaciones
    
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
                    <p>Puedes acceder al sistema en el siguiente enlace:</p>
                    <a href="http://localhost:8000/docs" style="display: inline-block; padding: 12px 24px; background-color: #2e86de; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0;">Acceder al Sistema</a>
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
                    <p>Puedes ver el detalle completo en el sistema.</p>
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
                    <p>Puedes descargarlo desde el sistema en la sección de materiales.</p>
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
                    <p>Se ha registrado tu asistencia para la siguiente clase:</p>
                    <div style="background-color: white; padding: 20px; border-left: 4px solid {color}; margin: 20px 0;">
                        <p><strong>Curso:</strong> {curso}</p>
                        <p><strong>Fecha:</strong> {fecha}</p>
                        <p><strong>Estado:</strong> <span style="font-size: 20px;">{estado}</span></p>
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
                    <p>Puedes ver el horario y más detalles en el sistema.</p>
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
