"""
test_int_cursos.py
Pruebas de integración para el endpoint /cursos/
Requiere docente creado previamente (relación FK id_docente).
Técnicas: Clases de Equivalencia (CE), Valores Límite (VL), Camino Básico (CB)
"""
import pytest

# ─── Datos de prueba únicos para esta suite ──────────────────────────────────
_DOCENTE_CURSOS = {
    "nombres": "Beatriz",
    "apellidos": "Mendoza",
    "cedula": "30030030",
    "correo": "beatriz.mendoza.cur@gmail.com",
    "contraseña": "DocCursos2024!",
    "especialidad": "Física",
    "estado": True,
}

_id_docente_cur = None
_id_curso       = None


class TestCursosIntegracion:

    # ── Preparación: docente requerido como FK ────────────────────────────

    def test_PREP01_crear_docente_para_cursos(self, client):
        """PREP-01 | Crear docente que actúa como FK en los cursos → 201"""
        global _id_docente_cur
        resp = client.post("/docentes/", json=_DOCENTE_CURSOS)
        assert resp.status_code == 201
        _id_docente_cur = resp.json()["id_docente"]

    # ── Clases de Equivalencia ──────────────────────────────────────────────

    def test_CE01_crear_curso_valido_retorna_201(self, client):
        """CE-01 | POST /cursos/ con datos completos → 201 y id_curso presente"""
        global _id_curso
        payload = {
            "nombre": "Álgebra Lineal",
            "cupo_estudiante": 30,
            "horario": [{"dia": "Lunes", "hora": "08:00"}],
            "id_docente": _id_docente_cur,
            "estado": True,
        }
        resp = client.post("/cursos/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Álgebra Lineal"
        assert "id_curso" in data
        _id_curso = data["id_curso"]

    def test_CE02_cupo_cero_rechazado_422(self, client):
        """CE-02 | cupo_estudiante=0 → 422 (el validador exige mínimo 1)"""
        payload = {
            "nombre": "Curso Invalido",
            "cupo_estudiante": 0,
            "horario": [{"dia": "Martes", "hora": "10:00"}],
            "id_docente": _id_docente_cur,
        }
        resp = client.post("/cursos/", json=payload)
        assert resp.status_code == 422

    def test_CE03_horario_vacio_rechazado_422(self, client):
        """CE-03 | horario=[] vacío → 422 (debe tener al menos un bloque)"""
        payload = {
            "nombre": "Curso Sin Horario",
            "cupo_estudiante": 20,
            "horario": [],
            "id_docente": _id_docente_cur,
        }
        resp = client.post("/cursos/", json=payload)
        assert resp.status_code == 422

    def test_CE04_listar_cursos_retorna_200(self, client):
        """CE-04 | GET /cursos/ → 200 y la lista tiene al menos un registro"""
        resp = client.get("/cursos/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_CE05_obtener_curso_por_id_retorna_200(self, client):
        """CE-05 | GET /cursos/{id} con ID válido → 200 y datos coinciden"""
        resp = client.get(f"/cursos/{_id_curso}")
        assert resp.status_code == 200
        assert resp.json()["id_curso"] == _id_curso

    def test_CE06_obtener_id_inexistente_retorna_404(self, client):
        """CE-06 | GET /cursos/999999 → 404"""
        resp = client.get("/cursos/999999")
        assert resp.status_code == 404

    # ── Valores Límite ──────────────────────────────────────────────────────

    def test_VL01_cupo_minimo_uno_es_valido(self, client):
        """VL-01 | cupo_estudiante=1 (mínimo permitido) → 201"""
        payload = {
            "nombre": "Curso Minimo",
            "cupo_estudiante": 1,
            "horario": [{"dia": "Viernes", "hora": "14:00"}],
            "id_docente": _id_docente_cur,
        }
        resp = client.post("/cursos/", json=payload)
        assert resp.status_code == 201
        # Limpiar el registro temporal
        nuevo_id = resp.json()["id_curso"]
        client.delete(f"/cursos/{nuevo_id}")

    def test_VL02_cupo_negativo_rechazado_422(self, client):
        """VL-02 | cupo_estudiante=-5 → 422"""
        payload = {
            "nombre": "Curso Negativo",
            "cupo_estudiante": -5,
            "horario": [{"dia": "Martes", "hora": "09:00"}],
            "id_docente": _id_docente_cur,
        }
        resp = client.post("/cursos/", json=payload)
        assert resp.status_code == 422

    # ── Camino Básico ───────────────────────────────────────────────────────

    def test_CB01_actualizar_nombre_curso(self, client):
        """CB-01 | PUT /cursos/{id} → cambia nombre → 200 con datos actualizados"""
        resp = client.put(f"/cursos/{_id_curso}", json={"nombre": "Álgebra Lineal II"})
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Álgebra Lineal II"

    def test_CB02_eliminar_curso_existente(self, client):
        """CB-02 | DELETE /cursos/{id} → 204 No Content"""
        resp = client.delete(f"/cursos/{_id_curso}")
        assert resp.status_code == 204

    def test_CB03_obtener_curso_eliminado_retorna_404(self, client):
        """CB-03 | GET /cursos/{id} tras DELETE → 404 (ya no existe)"""
        resp = client.get(f"/cursos/{_id_curso}")
        assert resp.status_code == 404
