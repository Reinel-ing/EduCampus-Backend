import requests
from datetime import date

BASE_URL = "https://educampus-backend.onrender.com"

def seed_docentes():
    docentes = [
        {"nombres": "Carlos", "apellidos": "Perez", "cedula": "1234567890", "correo": "carlos.perez@outlook.com", "contraseña": "docente123", "especialidad": "Matematicas", "estado": True},
        {"nombres": "Maria", "apellidos": "Gonzalez", "cedula": "0987654321", "correo": "maria.gonzalez@outlook.com", "contraseña": "docente123", "especialidad": "Fisica", "estado": True},
        {"nombres": "Juan", "apellidos": "Rodriguez", "cedula": "1122334455", "correo": "juan.rodriguez@outlook.com", "contraseña": "docente123", "especialidad": "Programacion", "estado": True},
    ]
    ids = []
    for d in docentes:
        r = requests.post(f"{BASE_URL}/docentes/", json=d)
        if r.status_code == 201:
            ids.append(r.json()["id_docente"])
            print(f"Docente {d['nombres']}: OK")
        else:
            print(f"Docente {d['nombres']}: {r.status_code} {r.text}")
    return ids

def seed_estudiantes():
    estudiantes = [
        {"nombres": "Ana", "apellidos": "Martinez", "cedula": "2233445566", "correo": "ana.martinez@outlook.com", "contraseña": "estudiante123", "telefono": "0991234567", "estado": True},
        {"nombres": "Luis", "apellidos": "Hernandez", "cedula": "3344556677", "correo": "luis.hernandez@outlook.com", "contraseña": "estudiante123", "telefono": "0992345678", "estado": True},
        {"nombres": "Sofia", "apellidos": "Lopez", "cedula": "4455667788", "correo": "sofia.lopez@outlook.com", "contraseña": "estudiante123", "telefono": "0993456789", "estado": True},
        {"nombres": "Pedro", "apellidos": "Garcia", "cedula": "5566778899", "correo": "pedro.garcia@outlook.com", "contraseña": "estudiante123", "telefono": "0994567890", "estado": True},
        {"nombres": "Laura", "apellidos": "Diaz", "cedula": "6677889900", "correo": "laura.diaz@outlook.com", "contraseña": "estudiante123", "telefono": "0995678901", "estado": True},
    ]
    ids = []
    for e in estudiantes:
        r = requests.post(f"{BASE_URL}/estudiantes/", json=e)
        if r.status_code == 201:
            ids.append(r.json()["id_estudiante"])
            print(f"Estudiante {e['nombres']}: OK")
        else:
            print(f"Estudiante {e['nombres']}: {r.status_code} {r.text}")
    return ids

def seed_cursos(docente_ids):
    cursos = [
        {"nombre": "Calculo I", "cupo_estudiante": 30, "horario": [{"dia": "Lunes", "hora": "08:00-10:00"}, {"dia": "Miercoles", "hora": "08:00-10:00"}], "id_docente": docente_ids[0], "estado": True},
        {"nombre": "Fisica General", "cupo_estudiante": 25, "horario": [{"dia": "Martes", "hora": "10:00-12:00"}, {"dia": "Jueves", "hora": "10:00-12:00"}], "id_docente": docente_ids[1], "estado": True},
        {"nombre": "Programacion Python", "cupo_estudiante": 20, "horario": [{"dia": "Viernes", "hora": "14:00-18:00"}], "id_docente": docente_ids[2], "estado": True},
    ]
    ids = []
    for c in cursos:
        r = requests.post(f"{BASE_URL}/cursos/", json=c)
        if r.status_code == 201:
            ids.append(r.json()["id_curso"])
            print(f"Curso {c['nombre']}: OK")
        else:
            print(f"Curso {c['nombre']}: {r.status_code} {r.text}")
    return ids

def seed_inscripciones(est_ids, cur_ids):
    pares = [
        (est_ids[0], cur_ids[0]), (est_ids[0], cur_ids[1]),
        (est_ids[1], cur_ids[0]), (est_ids[1], cur_ids[2]),
        (est_ids[2], cur_ids[1]), (est_ids[2], cur_ids[2]),
        (est_ids[3], cur_ids[0]), (est_ids[4], cur_ids[2]),
    ]
    for id_e, id_c in pares:
        r = requests.post(f"{BASE_URL}/inscripciones/", json={"id_estudiante": id_e, "id_curso": id_c})
        print(f"Inscripcion e{id_e} c{id_c}: {r.status_code}")

def seed_calificaciones(est_ids, cur_ids):
    cals = [
        (est_ids[0], cur_ids[0], 1, 4.5), (est_ids[0], cur_ids[0], 2, 4.2),
        (est_ids[0], cur_ids[1], 1, 3.8), (est_ids[1], cur_ids[0], 1, 4.0),
        (est_ids[1], cur_ids[2], 1, 4.7), (est_ids[2], cur_ids[1], 1, 3.5),
        (est_ids[2], cur_ids[2], 1, 4.3), (est_ids[3], cur_ids[0], 1, 3.9),
        (est_ids[4], cur_ids[2], 1, 4.1),
    ]
    for id_e, id_c, tipo, nota in cals:
        r = requests.post(f"{BASE_URL}/calificaciones/", json={"id_estudiante": id_e, "id_curso": id_c, "tipo_evaluacion": tipo, "nota": nota})
        print(f"Calificacion e{id_e} c{id_c} nota{nota}: {r.status_code}")

def seed_asistencias(est_ids, cur_ids):
    asists = [
        (est_ids[0], cur_ids[0], "2025-11-01", True),  (est_ids[0], cur_ids[0], "2025-11-03", True),
        (est_ids[0], cur_ids[0], "2025-11-05", False), (est_ids[1], cur_ids[0], "2025-11-01", True),
        (est_ids[1], cur_ids[2], "2025-11-02", True),  (est_ids[2], cur_ids[1], "2025-11-02", True),
        (est_ids[2], cur_ids[2], "2025-11-02", True),  (est_ids[3], cur_ids[0], "2025-11-03", True),
        (est_ids[4], cur_ids[2], "2025-11-04", True),
    ]
    for id_e, id_c, fecha, estado in asists:
        r = requests.post(f"{BASE_URL}/asistencia/", json={"id_estudiante": id_e, "id_curso": id_c, "fecha": fecha, "estado": estado})
        print(f"Asistencia e{id_e} c{id_c}: {r.status_code}")

if __name__ == "__main__":
    print("Restaurando docentes...")
    docente_ids = seed_docentes()
    print("\nRestaurando estudiantes...")
    estudiante_ids = seed_estudiantes()
    if docente_ids and estudiante_ids:
        print("\nRestaurando cursos...")
        curso_ids = seed_cursos(docente_ids)
        print("\nRestaurando inscripciones...")
        seed_inscripciones(estudiante_ids, curso_ids)
        print("\nRestaurando calificaciones...")
        seed_calificaciones(estudiante_ids, curso_ids)
        print("\nRestaurando asistencias...")
        seed_asistencias(estudiante_ids, curso_ids)
    print("\nListo.")
