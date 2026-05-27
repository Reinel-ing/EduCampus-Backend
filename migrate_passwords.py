# -*- coding: utf-8 -*-
"""
Script de migracion de contrasenas - EduCampus
===============================================
Ejecutar desde la carpeta API-EduCampus:
    python migrate_passwords.py

Asigna la contrasena 'EduCampus2025' a todos los usuarios
usando el nuevo esquema seguro: SHA-256 -> bcrypt+salt -> BD
"""
import sys
import os
import hashlib
import bcrypt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.db import SessionLocal
from models.docente import Docente
from models.estudiante import Estudiante
from models.administrador import Administrador

# Nombre del campo con la n-tilde (compatible con Windows cp1252)
CAMPO = "contrase" + chr(241) + "a"

DEFAULT_PASSWORD = "EduCampus2025"


def sha256_hex(text):
    """Mismo calculo que hace crypto.subtle.digest en el frontend"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def nuevo_hash(plain_password):
    """SHA-256 -> bcrypt con salt aleatorio -> hash unico"""
    sha = sha256_hex(plain_password)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(sha.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def migrar(password=DEFAULT_PASSWORD):
    db = SessionLocal()
    try:
        print("=" * 55)
        print("Migracion de contrasenas EduCampus - SHA-256 + bcrypt")
        print("=" * 55)
        print("Contrasena asignada a todos: {}".format(password))

        for a in db.query(Administrador).all():
            setattr(a, CAMPO, nuevo_hash(password))
            print("  [Admin]      {}".format(a.correo))

        for d in db.query(Docente).all():
            setattr(d, CAMPO, nuevo_hash(password))
            print("  [Docente]    {}".format(d.correo))

        for e in db.query(Estudiante).all():
            setattr(e, CAMPO, nuevo_hash(password))
            print("  [Estudiante] {}".format(e.correo))

        db.commit()
        print("\nMigracion completada exitosamente!")
        print("Cada usuario tiene un hash DISTINTO en la BD")
        print("aunque todos usen la misma contrasena (gracias al salt de bcrypt).")

    except Exception as ex:
        db.rollback()
        print("ERROR durante la migracion: {}".format(ex))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    pwd = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PASSWORD
    migrar(pwd)
