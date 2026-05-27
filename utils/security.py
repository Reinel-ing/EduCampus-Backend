import bcrypt

def hash_password(password: str) -> str:
    """
    Almacena la contraseña de forma segura usando bcrypt + salt aleatorio.

    El frontend ya envía SHA-256(contraseña_original), así que aquí
    recibimos un hash hex de 64 chars. bcrypt lo vuelve a hashear con
    un salt aleatorio diferente cada vez → aunque dos usuarios tengan
    la misma contraseña, el valor almacenado en la BD es SIEMPRE distinto.

    Flujo completo:
        [Usuario escribe] → SHA-256 (frontend) → bcrypt+salt (backend) → BD
    """
    password_bytes = password.encode("utf-8")
    # bcrypt.gensalt() genera un salt único cada llamada → hashes siempre distintos
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(input_password: str, hashed_password: str) -> bool:
    """
    Verifica que el SHA-256 enviado por el frontend coincida con el
    hash bcrypt almacenado en la BD.

    bcrypt.checkpw compara de forma segura (tiempo constante) para
    prevenir ataques de temporización.
    """
    try:
        password_bytes = input_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False
