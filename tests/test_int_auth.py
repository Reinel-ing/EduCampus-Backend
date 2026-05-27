"""
test_int_auth.py
Pruebas de integración para el endpoint /auth/login
Verifica que el sistema autentica correctamente a docentes y estudiantes.
Técnicas: Clases de Equivalencia (CE), Valores Límite (VL), Camino Básico (CB)
"""
import pytest

# ─── Datos de prueba únicos para esta suite ──────────────────────────────────
_DOCENTE_AUTH = {
    "nombres": "Carlos",
    "apellidos": "Ruiz",
    "cedula": "20020020",
    "correo": "carlos.ruiz.auth@gmail.com",
    "contraseña": "DocAuth2024!",
    "especialidad": "Matemáticas",
    "estado": True,
}

_ESTUDIANTE_AUTH = {
    "nombres": "Ana",
    "apellidos": "Lopez",
    "cedula": "20020021",
    "correo": "ana.lopez.auth@gmail.com",
    "contraseña": "EstAuth2024!",
    "telefono": "3201234567",
    "estado": True,
}

_id_docente_auth  = None
_id_est_auth      = None


class TestAuthIntegracion:

    # ── Preparación: crear los usuarios que se usarán en el login ────────

    def test_PREP01_crear_docente_para_pruebas_login(self, client):
        """PREP-01 | Crear docente de prueba → 201"""
        global _id_docente_auth
        resp = client.post("/docentes/", json=_DOCENTE_AUTH)
        assert resp.status_code == 201
        _id_docente_auth = resp.json()["id_docente"]

    def test_PREP02_crear_estudiante_para_pruebas_login(self, client):
        """PREP-02 | Crear estudiante de prueba → 201"""
        global _id_est_auth
        resp = client.post("/estudiantes/", json=_ESTUDIANTE_AUTH)
        assert resp.status_code == 201
        _id_est_auth = resp.json()["id_estudiante"]

    # ── Clases de Equivalencia ──────────────────────────────────────────────

    def test_CE01_login_docente_valido_retorna_200(self, client):
        """CE-01 | Credenciales de docente correctas → 200 y rol='docente'"""
        resp = client.post("/auth/login", json={
            "correo": _DOCENTE_AUTH["correo"],
            "contraseña": _DOCENTE_AUTH["contraseña"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["rol"] == "docente"
        assert data["correo"] == _DOCENTE_AUTH["correo"].lower()

    def test_CE02_login_estudiante_valido_retorna_200(self, client):
        """CE-02 | Credenciales de estudiante correctas → 200 y rol='estudiante'"""
        resp = client.post("/auth/login", json={
            "correo": _ESTUDIANTE_AUTH["correo"],
            "contraseña": _ESTUDIANTE_AUTH["contraseña"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["rol"] == "estudiante"

    def test_CE03_contraseña_incorrecta_retorna_401(self, client):
        """CE-03 | Contraseña equivocada → 401 Unauthorized"""
        resp = client.post("/auth/login", json={
            "correo": _ESTUDIANTE_AUTH["correo"],
            "contraseña": "claveIncorrecta999",
        })
        assert resp.status_code == 401

    def test_CE04_correo_no_registrado_retorna_401(self, client):
        """CE-04 | Correo que no existe en el sistema → 401"""
        resp = client.post("/auth/login", json={
            "correo": "noexiste@gmail.com",
            "contraseña": "cualquier",
        })
        assert resp.status_code == 401

    # ── Valores Límite ──────────────────────────────────────────────────────

    def test_VL01_contraseña_vacia_retorna_401(self, client):
        """VL-01 | Contraseña vacía → 401 (no puede autenticarse sin clave)"""
        resp = client.post("/auth/login", json={
            "correo": _ESTUDIANTE_AUTH["correo"],
            "contraseña": "",
        })
        assert resp.status_code == 401

    def test_VL02_correo_vacio_retorna_401(self, client):
        """VL-02 | Correo vacío → 401"""
        resp = client.post("/auth/login", json={
            "correo": "",
            "contraseña": "cualquier",
        })
        assert resp.status_code == 401

    # ── Camino Básico ───────────────────────────────────────────────────────

    def test_CB01_login_estudiante_devuelve_id_correcto(self, client):
        """CB-01 | Login estudiante → el campo 'id' coincide con el ID asignado al crear"""
        resp = client.post("/auth/login", json={
            "correo": _ESTUDIANTE_AUTH["correo"],
            "contraseña": _ESTUDIANTE_AUTH["contraseña"],
        })
        assert resp.status_code == 200
        assert resp.json()["id"] == _id_est_auth

    def test_CB02_login_docente_devuelve_especialidad(self, client):
        """CB-02 | Login docente → la especialidad está presente en la respuesta"""
        resp = client.post("/auth/login", json={
            "correo": _DOCENTE_AUTH["correo"],
            "contraseña": _DOCENTE_AUTH["contraseña"],
        })
        assert resp.status_code == 200
        assert resp.json()["especialidad"] == _DOCENTE_AUTH["especialidad"]
