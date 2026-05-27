import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

tablas = [
    "entregas_actividad",
    "notificaciones",
    "actividades",
    "evento",
    "material_didactico",
    "asistencia",
    "calificacion",
    "estudiante_curso",
    "curso",
    "estudiante",
    "docente",
    "configuracion",
]

for tabla in tablas:
    cur.execute(f'TRUNCATE TABLE "{tabla}" CASCADE')
    print(f"Limpiada: {tabla}")

conn.commit()
cur.close()
conn.close()
print("Base de datos limpia. Administrador conservado.")
