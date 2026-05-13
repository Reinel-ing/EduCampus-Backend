import requests
from datetime import date, datetime

BASE_URL = "http://127.0.0.1:8000"

def seed_configuracion():
    data = {
        "nombre_institucion": "Instituto Tecnológico Vortal",
        "email_contacto": "contacto@vortal.edu",
        "ano_academico": "2025"
    }
    response = requests.post(f"{BASE_URL}/configuracion/", json=data)
    print(f"Configuración: {response.status_code}")

def seed_docentes():
    # Las contraseñas se hashearán automáticamente en el backend
    docentes = [
        {"nombres": "Carlos", "apellidos": "Pérez", "cedula": "1234567890", "correo": "carlos.perez@vortal.edu", "contraseña": "docente123", "especialidad": "Matemáticas", "estado": True},
        {"nombres": "María", "apellidos": "González", "cedula": "0987654321", "correo": "maria.gonzalez@vortal.edu", "contraseña": "docente123", "especialidad": "Física", "estado": True},
        {"nombres": "Juan", "apellidos": "Rodríguez", "cedula": "1122334455", "correo": "juan.rodriguez@vortal.edu", "contraseña": "docente123", "especialidad": "Programación", "estado": True}
    ]
    ids = []
    for docente in docentes:
        response = requests.post(f"{BASE_URL}/docentes/", json=docente)
        if response.status_code == 201:
            ids.append(response.json()["id_docente"])
            print(f"Docente {docente['nombres']}: {response.status_code}")
    return ids

def seed_estudiantes():
    # Las contraseñas se hashearán automáticamente en el backend
    estudiantes = [
        {"nombres": "Ana", "apellidos": "Martínez", "cedula": "2233445566", "correo": "ana.martinez@estudiante.edu", "contraseña": "estudiante123", "telefono": "0991234567", "estado": True},
        {"nombres": "Luis", "apellidos": "Hernández", "cedula": "3344556677", "correo": "luis.hernandez@estudiante.edu", "contraseña": "estudiante123", "telefono": "0992345678", "estado": True},
        {"nombres": "Sofía", "apellidos": "López", "cedula": "4455667788", "correo": "sofia.lopez@estudiante.edu", "contraseña": "estudiante123", "telefono": "0993456789", "estado": True},
        {"nombres": "Pedro", "apellidos": "García", "cedula": "5566778899", "correo": "pedro.garcia@estudiante.edu", "contraseña": "estudiante123", "telefono": "0994567890", "estado": True},
        {"nombres": "Laura", "apellidos": "Díaz", "cedula": "6677889900", "correo": "laura.diaz@estudiante.edu", "contraseña": "estudiante123", "telefono": "0995678901", "estado": True}
    ]
    ids = []
    for estudiante in estudiantes:
        response = requests.post(f"{BASE_URL}/estudiantes/", json=estudiante)
        if response.status_code == 201:
            ids.append(response.json()["id_estudiante"])
            print(f"Estudiante {estudiante['nombres']}: {response.status_code}")
    return ids

def seed_cursos(docente_ids):
    cursos = [
        {"nombre": "Cálculo I", "cupo_estudiante": 30, "horario": [{"dia": "Lunes", "hora": "08:00-10:00"}, {"dia": "Miércoles", "hora": "08:00-10:00"}], "id_docente": docente_ids[0], "estado": True},
        {"nombre": "Física General", "cupo_estudiante": 25, "horario": [{"dia": "Martes", "hora": "10:00-12:00"}, {"dia": "Jueves", "hora": "10:00-12:00"}], "id_docente": docente_ids[1], "estado": True},
        {"nombre": "Programación Python", "cupo_estudiante": 20, "horario": [{"dia": "Viernes", "hora": "14:00-18:00"}], "id_docente": docente_ids[2], "estado": True}
    ]
    ids = []
    for curso in cursos:
        response = requests.post(f"{BASE_URL}/cursos/", json=curso)
        if response.status_code == 201:
            ids.append(response.json()["id_curso"])
            print(f"Curso {curso['nombre']}: {response.status_code}")
    return ids

def seed_inscripciones(estudiante_ids, curso_ids):
    inscripciones = [
        {"id_estudiante": estudiante_ids[0], "id_curso": curso_ids[0]},
        {"id_estudiante": estudiante_ids[0], "id_curso": curso_ids[1]},
        {"id_estudiante": estudiante_ids[1], "id_curso": curso_ids[0]},
        {"id_estudiante": estudiante_ids[1], "id_curso": curso_ids[2]},
        {"id_estudiante": estudiante_ids[2], "id_curso": curso_ids[1]},
        {"id_estudiante": estudiante_ids[2], "id_curso": curso_ids[2]},
        {"id_estudiante": estudiante_ids[3], "id_curso": curso_ids[0]},
        {"id_estudiante": estudiante_ids[4], "id_curso": curso_ids[2]}
    ]
    for inscripcion in inscripciones:
        response = requests.post(f"{BASE_URL}/inscripciones/", json=inscripcion)
        print(f"Inscripción estudiante {inscripcion['id_estudiante']} a curso {inscripcion['id_curso']}: {response.status_code}")

def seed_calificaciones(estudiante_ids, curso_ids):
    calificaciones = [
        {"id_estudiante": estudiante_ids[0], "id_curso": curso_ids[0], "tipo_evaluacion": 1, "nota": 4.5},
        {"id_estudiante": estudiante_ids[0], "id_curso": curso_ids[0], "tipo_evaluacion": 2, "nota": 4.2},
        {"id_estudiante": estudiante_ids[0], "id_curso": curso_ids[1], "tipo_evaluacion": 1, "nota": 3.8},
        {"id_estudiante": estudiante_ids[1], "id_curso": curso_ids[0], "tipo_evaluacion": 1, "nota": 4.0},
        {"id_estudiante": estudiante_ids[1], "id_curso": curso_ids[2], "tipo_evaluacion": 1, "nota": 4.7},
        {"id_estudiante": estudiante_ids[2], "id_curso": curso_ids[1], "tipo_evaluacion": 1, "nota": 3.5},
        {"id_estudiante": estudiante_ids[2], "id_curso": curso_ids[2], "tipo_evaluacion": 1, "nota": 4.3}
    ]
    for calificacion in calificaciones:
        response = requests.post(f"{BASE_URL}/calificaciones/", json=calificacion)
        print(f"Calificación: {response.status_code}")

def seed_asistencias(estudiante_ids, curso_ids):
    asistencias = [
        {"id_estudiante": estudiante_ids[0], "id_curso": curso_ids[0], "fecha": "2025-11-01", "estado": True},
        {"id_estudiante": estudiante_ids[0], "id_curso": curso_ids[0], "fecha": "2025-11-03", "estado": True},
        {"id_estudiante": estudiante_ids[0], "id_curso": curso_ids[0], "fecha": "2025-11-05", "estado": False},
        {"id_estudiante": estudiante_ids[1], "id_curso": curso_ids[0], "fecha": "2025-11-01", "estado": True},
        {"id_estudiante": estudiante_ids[1], "id_curso": curso_ids[2], "fecha": "2025-11-02", "estado": True},
        {"id_estudiante": estudiante_ids[2], "id_curso": curso_ids[1], "fecha": "2025-11-02", "estado": True},
        {"id_estudiante": estudiante_ids[2], "id_curso": curso_ids[2], "fecha": "2025-11-02", "estado": True}
    ]
    for asistencia in asistencias:
        response = requests.post(f"{BASE_URL}/asistencia/", json=asistencia)
        print(f"Asistencia: {response.status_code}")

def seed_material(curso_ids):
    materiales = [
        {"id_curso": curso_ids[0], "archivo_url": "https://ejemplo.com/calculo1.pdf", "nombre_archivo": "Guía Cálculo I", "fecha": str(date.today())},
        {"id_curso": curso_ids[1], "archivo_url": "https://ejemplo.com/fisica.pdf", "nombre_archivo": "Manual Física", "fecha": str(date.today())},
        {"id_curso": curso_ids[2], "archivo_url": "https://ejemplo.com/python.pdf", "nombre_archivo": "Tutorial Python", "fecha": str(date.today())}
    ]
    for material in materiales:
        response = requests.post(f"{BASE_URL}/material/upload", json=material)
        print(f"Material: {response.status_code}")

if __name__ == "__main__":
    print("🌱 Iniciando seed de datos...\n")
    
    print("📋 Creando configuración...")
    seed_configuracion()
    
    print("\n👨‍🏫 Creando docentes...")
    docente_ids = seed_docentes()
    
    print("\n👨‍🎓 Creando estudiantes...")
    estudiante_ids = seed_estudiantes()
    
    print("\n📚 Creando cursos...")
    curso_ids = seed_cursos(docente_ids)
    
    print("\n✍️ Creando inscripciones...")
    seed_inscripciones(estudiante_ids, curso_ids)
    
    print("\n📝 Creando calificaciones...")
    seed_calificaciones(estudiante_ids, curso_ids)
    
    print("\n📊 Creando asistencias...")
    seed_asistencias(estudiante_ids, curso_ids)
    
    print("\n📄 Creando material didáctico...")
    seed_material(curso_ids)
    
    print("\n✅ Seed completado exitosamente!")
