"""
notificacion_service.py
Funciones auxiliares para crear notificaciones en base de datos.

Estos helpers son llamados desde los routers después de cada acción
relevante (nueva matrícula, calificación publicada, material subido, etc.).
No hacen commit por sí solos; el router que los invoca es responsable
de confirmar la transacción.
"""

from models.notificacion import Notificacion


def crear_notificacion(db, titulo: str, mensaje: str, tipo: str,
                       id_destinatario: int, tipo_destinatario: str) -> None:
    """
    Inserta una notificación en la sesión activa para un usuario específico.

    Args:
        db: Sesión de SQLAlchemy (sin commit).
        titulo: Título corto de la notificación.
        mensaje: Cuerpo del mensaje.
        tipo: Categoría ('info', 'calificacion', 'material', 'inscripcion', etc.).
        id_destinatario: ID del usuario receptor.
        tipo_destinatario: Rol del receptor ('admin', 'docente', 'estudiante').
    """
    try:
        notificacion = Notificacion(
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            id_destinatario=id_destinatario,
            tipo_destinatario=tipo_destinatario,
        )
        db.add(notificacion)
    except Exception as exc:
        print(f"[notificacion_service] Error al crear notificación: {exc}")


def notificar_admins(db, titulo: str, mensaje: str, tipo: str = "info") -> None:
    """
    Crea la misma notificación para todos los administradores registrados.

    Útil para informar al equipo administrativo sobre eventos del sistema
    (nuevas inscripciones, entregas de actividades, etc.).

    Args:
        db: Sesión de SQLAlchemy (sin commit).
        titulo: Título de la notificación.
        mensaje: Cuerpo del mensaje.
        tipo: Categoría de la notificación (por defecto 'info').
    """
    try:
        from models.administrador import Administrador
        admins = db.query(Administrador).all()
        for admin in admins:
            notificacion = Notificacion(
                titulo=titulo,
                mensaje=mensaje,
                tipo=tipo,
                id_destinatario=admin.id_administrador,
                tipo_destinatario="admin",
            )
            db.add(notificacion)
    except Exception as exc:
        print(f"[notificacion_service] Error al notificar admins: {exc}")
