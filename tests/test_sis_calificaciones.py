"""
test_sis_calificaciones.py
Pruebas de sistema para el módulo de calificaciones.
Verifica el registro, actualización y cálculo de promedios de notas,
con validación de reglas de negocio (escala 0.0–5.0 colombiana).
Técnicas: Clases de Equivalencia (CE), Valores Límite (VL), Camino Básico (CB)
"""
import pytest

# ─── Datos únicos para esta suite ────────────────────────────────────────────
_DOCENTE_CAL = {
    "nombres": "Diana",
    "apellidos": "Castro",
    "cedula": "60060060",
    "correo": "diana.castro.cal@gmail.com",
    "contraseña": "DocCal2024!",
    "especialidad": "Quimica",
    "estado": True,
}

_ESTUDIANTE_CAL = {
    "nombres": "Manuel",
    "apellidos": "Reyes",
    "cedula": "60060061",
    "correo": "manuel.reyes.cal@gmail.com",
    "contraseña": "EstCal2024!",
    "estado": True,
}

_sis_cal = {}   # IDs compartidos entre pasos


class TestSistemaCalificaciones:

    # ── Preparación ───────────────────────────────────────────────────────

    def test_SETUP01_crear_docente_curso_estudiante_e_inscribir(self, client):
        """SETUP-01 | Crear todos los datos previos y dejar al estudiante inscrito"""
        # Docente
        resp_doc = client.post("/docentes/", json=_DOCENTE_CAL)
        assert resp_doc.status_code == 201
        _sis_cal["id_docente"] = resp_doc.json()["id_docente"]

        # Curso
        resp_cur = client.post("/cursos/", json={
            "nombre": "Quimica Organica",
            "cupo_estudiante": 10,
            "horario": [{"dia": "Martes", "hora": "11:00"}],
            "id_docente": _sis_cal["id_docente"],
            "estado": True,
        })
        assert resp_cur.status_code == 201
        _sis_cal["id_curso"] = resp_cur.json()["id_curso"]

        # Estudiante
        resp_est = client.post("/estudiantes/", json=_ESTUDIANTE_CAL)
        assert resp_est.status_code == 201
        _sis_cal["id_estudiante"] = resp_est.json()["id_estudiante"]

        # Inscripción
        resp_ins = client.post("/inscripciones/", json={
            "id_estudiante": _sis_cal["id_estudiante"],
            "id_curso":      _sis_cal["id_curso"],
        })
        assert resp_ins.status_code == 201

    # ── Clases de Equivalencia ────────────────────────────────────────────

    def test_CE01_registrar_nota_valida_retorna_201(self, client):
        """CE-01 | POST /calificaciones/ nota=3.5 → 201 y id asignado"""
        resp = client.post("/calificaciones/", json={
            "id_estudiante":  _sis_cal["id_estudiante"],
            "id_curso":       _sis_cal["id_curso"],
            "tipo_evaluacion": 1,
            "nota": 3.5,
        })
        assert resp.status_code == 201
        _sis_cal["id_cal_p1"] = resp.json()["id_calificacion"]

    def test_CE02_nota_negativa_rechazada_422(self, client):
        """CE-02 | nota=-1.0 → 422 (el validador Pydantic rechaza notas < 0)"""
        resp = client.post("/calificaciones/", json={
            "id_estudiante":  _sis_cal["id_estudiante"],
            "id_curso":       _sis_cal["id_curso"],
            "tipo_evaluacion": 2,
            "nota": -1.0,
        })
        assert resp.status_code == 422

    def test_CE03_nota_mayor_cinco_rechazada_422(self, client):
        """CE-03 | nota=6.0 → 422 (el validador Pydantic rechaza notas > 5)"""
        resp = client.post("/calificaciones/", json={
            "id_estudiante":  _sis_cal["id_estudiante"],
            "id_curso":       _sis_cal["id_curso"],
            "tipo_evaluacion": 2,
            "nota": 6.0,
        })
        assert resp.status_code == 422

    def test_CE04_registrar_segundo_parcial(self, client):
        """CE-04 | Registrar segundo parcial nota=4.0 → 201"""
        resp = client.post("/calificaciones/", json={
            "id_estudiante":  _sis_cal["id_estudiante"],
            "id_curso":       _sis_cal["id_curso"],
            "tipo_evaluacion": 2,
            "nota": 4.0,
        })
        assert resp.status_code == 201

    # ── Valores Límite ────────────────────────────────────────────────────

    def test_VL01_nota_cero_es_valida(self, client):
        """VL-01 | nota=0.0 (mínimo permitido) → 201"""
        resp = client.post("/calificaciones/", json={
            "id_estudiante":  _sis_cal["id_estudiante"],
            "id_curso":       _sis_cal["id_curso"],
            "tipo_evaluacion": 3,
            "nota": 0.0,
        })
        assert resp.status_code == 201
        _sis_cal["id_cal_final"] = resp.json()["id_calificacion"]

    def test_VL02_nota_cinco_es_valida(self, client):
        """VL-02 | nota=5.0 (máximo permitido) → 201"""
        resp = client.post("/calificaciones/", json={
            "id_estudiante":  _sis_cal["id_estudiante"],
            "id_curso":       _sis_cal["id_curso"],
            "tipo_evaluacion": 1,
            "nota": 5.0,
        })
        assert resp.status_code == 201

    # ── Camino Básico ─────────────────────────────────────────────────────

    def test_CB01_listar_calificaciones_del_estudiante(self, client):
        """CB-01 | GET /calificaciones/por-estudiante/{id} → lista no vacía"""
        resp = client.get(f"/calificaciones/por-estudiante/{_sis_cal['id_estudiante']}")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_CB02_promedio_del_estudiante_es_numerico(self, client):
        """CB-02 | GET /calificaciones/promedio-estudiante/{id} → valor entre 0 y 5"""
        resp = client.get(f"/calificaciones/promedio-estudiante/{_sis_cal['id_estudiante']}")
        assert resp.status_code == 200
        data = resp.json()
        assert "promedio" in data
        assert data["promedio"] is not None
        assert 0.0 <= data["promedio"] <= 5.0

    def test_CB03_actualizar_nota_existente(self, client):
        """CB-03 | PUT /calificaciones/{id} nota=4.5 → 200 con nota actualizada"""
        resp = client.put(f"/calificaciones/{_sis_cal['id_cal_p1']}", json={"nota": 4.5})
        assert resp.status_code == 200
        assert float(resp.json()["nota"]) == 4.5

    def test_CB04_promedio_por_curso_es_numerico(self, client):
        """CB-04 | GET /calificaciones/promedio-curso/{id} → promedio calculado"""
        resp = client.get(f"/calificaciones/promedio-curso/{_sis_cal['id_curso']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["promedio"] is not None
        assert 0.0 <= data["promedio"] <= 5.0
