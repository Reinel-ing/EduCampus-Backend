# -*- coding: utf-8 -*-
"""
set_password.py  -  Cambia la contrasena de UN usuario
=======================================================
Uso (desde la carpeta API-EduCampus con el venv activo):

    python set_password.py correo@gmail.com MiContrasena123

Funciona para administradores, docentes y estudiantes.
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

CAMPO = "contrase" + chr(241) + "a"


def sha256_hex(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def nuevo_hash(plain):
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(sha256_hex(plain).encode("utf-8"), salt).decode("utf-8")


def actualizar(correo, plain_password):
    db = SessionLocal()
    try:
        nuevo = nuevo_hash(plain_password)
        actualizado = False

        # Buscar en administradores
        a = db.query(Administrador).filter_by(correo=correo).first()
        if a:
            setattr(a, CAMPO, nuevo)
            db.commit()
            print("OK - Admin '{}' actualizado".format(correo))
            actualizado = True

        # Buscar en docentes
        d = db.query(Docente).filter_by(correo=correo).first()
        if d:
            setattr(d, CAMPO, nuevo)
            db.commit()
            print("OK - Docente '{}' actualizado".format(correo))
            actualizado = True

        # Buscar en estudiantes
        e = db.query(Estudiante).filter_by(correo=correo).first()
        if e:
            setattr(e, CAMPO, nuevo)
            db.commit()
            print("OK - Estudiante '{}' actualizado".format(correo))
            actualizado = True

        if not actualizado:
            print("ERROR - No se encontro el usuario: {}".format(correo))
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python set_password.py correo@gmail.com MiContrasena")
        print("")
        print("Usuarios en el sistema:")
        db = SessionLocal()
        for a in db.query(Administrador).all():
            print("  [Admin]      {}".format(a.correo))
        for d in db.query(Docente).all():
            print("  [Docente]    {}".format(d.correo))
        for e in db.query(Estudiante).all():
            print("  [Estudiante] {}".format(e.correo))
        db.close()
        sys.exit(1)

    correo_arg = sys.argv[1]
    password_arg = sys.argv[2]
    actualizar(correo_arg, password_arg)
