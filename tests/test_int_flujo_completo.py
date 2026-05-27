"""
test_int_flujo_completo.py
Pruebas de integración de flujo completo (escenario de usuario real).
Simula el ciclo: registrar docente → crear curso → registrar estudiante → login.
Técnicas: Camino Básico (CB), Regresión
"""
import pytest

# ─── Datos únicos para el flujo completo ─────────────────────────────────────
_DOCENTE_FLUJO = {
    "nombres": "Héctor",
    "apellidos": "Vargas",
    "cedula": "40040040",
    "correo": "hector.vargas.flujo@gmail.com",
    "contraseña": "DocFlujo2024!",
    "especialidad": "Programación",
    "estado": True,
}

_ESTUDIANTE_FLUJO = {
    "nombres": "Sofia",
    "apellidos": "Perez",
    "cedula": "40040041",
    "correo": "sofia.perez.flujo@gmail.com",
    "contraseña": "EstFlujo2024!",
    "telefono": "3001112233",
    "estado": True,
}

# Diccionario compartido para guardar IDs entre pasos del flujo
_flujo = {}


class TestFlujoCompletoIntegracion:

    def test_FLUJO01_registrar_docente(self, client):
        """FLUJO-01 | Registrar docente nuevo → 201, id asignado"""
        resp = client.post("/docentes/", json=_DOCENTE_FLUJO)
        assert resp.status_code == 201
        _flujo["id_docente"] = resp.json()["id_docente"]

    def test_FLUJO02_crear_curso_asignado_al_docente(self, client):
        """FLUJO-02 | Crear curso con el docente creado en paso anterior → 201"""
        payload = {
            "nombre": "Introducción a Python",
            "cupo_estudiante": 25,
            "horario": [
                {"dia": "Lunes",     "hora": "07:00"},
                {"dia": "Miércoles", "hora": "07:00"},
            ],
            "id_docente": _flujo["id_docente"],
            "estado": True,
        }
        resp = client.post("/cursos/", json=payload)
        assert resp.status_code == 201
        _flujo["id_curso"] = resp.json()["id_curso"]

    def test_FLUJO03_registrar_estudiante(self, client):
        """FLUJO-03 | Registrar estudiante nuevo → 201, id asignado"""
        resp = client.post("/estudiantes/", json=_ESTUDIANTE_FLUJO)
        assert resp.status_code == 201
        _flujo["id_estudiante"] = resp.json()["id_estudiante"]

    def test_FLUJO04_login_estudiante_recien_creado(self, client):
        """FLUJO-04 | El estudiante recién registrado puede hacer login → 200, rol='estudiante'"""
        resp = client.post("/auth/login", json={
            "correo":    _ESTUDIANTE_FLUJO["correo"],
            "contraseña": _ESTUDIANTE_FLUJO["contraseña"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["rol"] == "estudiante"
        assert data["id"] == _flujo["id_estudiante"]

    def test_FLUJO05_login_docente_recien_creado(self, client):
        """FLUJO-05 | El docente recién registrado puede hacer login → 200, rol='docente'"""
        resp = client.post("/auth/login", json={
            "correo":    _DOCENTE_FLUJO["correo"],
            "contraseña": _DOCENTE_FLUJO["contraseña"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["rol"] == "docente"
        assert data["id"] == _flujo["id_docente"]

    def test_FLUJO06_curso_aparece_en_listado_del_docente(self, client):
        """FLUJO-06 | GET /cursos/por-docente/{id} → el curso creado aparece en la lista"""
        resp = client.get(f"/cursos/por-docente/{_flujo['id_docente']}")
        assert resp.status_code == 200
        ids_cursos = [c["id_curso"] for c in resp.json()]
        assert _flujo["id_curso"] in ids_cursos
