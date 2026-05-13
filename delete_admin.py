from config.db import engine
from sqlalchemy import text
import sys

def delete_admin_by_email(email: str):
    with engine.begin() as conn:
        result = conn.execute(
            text("DELETE FROM administrador WHERE correo = :email RETURNING id_administrador"),
            {"email": email}
        )
        rows = result.fetchall()
        return rows

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        email = sys.argv[1]
    else:
        email = input("Ingrese el correo del administrador a eliminar: ").strip()

    if not email:
        print("No se proporcionó correo. Saliendo.")
        sys.exit(1)

    confirm = input(f"¿Eliminar administrador con correo '{email}'? (si/no): ")
    if confirm.lower() not in ("si", "s", "yes", "y"):
        print("Operación cancelada.")
        sys.exit(0)

    deleted = delete_admin_by_email(email)
    if deleted:
        ids = [r[0] for r in deleted]
        print(f"✅ Eliminado(s) administrador(es) con id(s): {ids}")
    else:
        print("ℹ️  No se encontró ningún administrador con ese correo.")
