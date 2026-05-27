"""
test_acep_historias_usuario.py
Pruebas de aceptación basadas en historias de usuario (HU).
Cada prueba corresponde a un criterio de aceptación definido desde
la perspectiva del usuario final del sistema EduCampus.

Técnica: Camino Básico (CB) orientado a historias de usuario
"""
import pytest

# ─── Datos únicos para esta suite ────────────────────────────────────────────
_DOCENTE_HU = {
    "nombres": "Patricia",
    "apellidos": "Suarez",
    "cedula": "70070070",
    "correo": "patricia.suarez.hu@gmail.com",
    "contraseña": "DocHU2024!",
    "especialidad": "Historia",
    "estado": True,
}

_ESTUDIANTE_HU = {
    "nombres": "Camilo",
    "apellidos": "Diaz",
    "cedula": "70070071",
    "correo": "camilo.diaz.hu@gmail.com",
    "contraseña": "EstHU2024!",
    "telefono": "3121234567",
    "estado": True,
}

_hu = {}   # IDs compartidos entre historias de usuario


# === HU-01 | Un estudiante puede registrarse y acceder al sistema ===
class TestHU01RegistroYLoginEstudiante:

    def test_HU01_paso1_registrar_estudiante(self, client):
        """HU-01/P1 | POST /estudiantes/ → estudiante registrado correctamente (201)"""
        resp = client.post("/estudiantes/", json=_ESTUDIANTE_HU)
        assert resp.status_code == 201
        data = resp.json()
        assert data["correo"] == _ESTUDIANTE_HU["correo"].lower()
        _hu["id_estudiante"] = data["id_estudiante"]

    def test_HU01_paso2_estudiante_puede_iniciar_sesion(self, client):
        """HU-01/P2 | El estudiante recién registrado puede iniciar sesión → rol='estudiante'"""
        resp = client.post("/auth/login", json={
            "correo":    _ESTUDIANTE_HU["correo"],
            "contraseña": _ESTUDIANTE_HU["contraseña"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["rol"] == "estudiante"
        assert data["id"]  == _hu["id_estudiante"]

    def test_HU01_paso3_credenciales_erroneas_bloquean_acceso(self, client):
        """HU-01/P3 | Contraseña incorrecta → 401, acceso denegado"""
        resp = client.post("/auth/login", json={
            "correo":    _ESTUDIANTE_HU["correo"],
            "contraseña": "claveErronea",
        })
        assert resp.status_code == 401


# === HU-02 | Un docente puede crear cursos y aparecer en el sistema ===
class TestHU02DocenteCreaYConsultaCurso:

    def test_HU02_paso1_registrar_docente(self, client):
        """HU-02/P1 | Docente se registra en el sistema → 201"""
        resp = client.post("/docentes/", json=_DOCENTE_HU)
        assert resp.status_code == 201
        _hu["id_docente"] = resp.json()["id_docente"]

    def test_HU02_paso2_docente_puede_iniciar_sesion(self, client):
        """HU-02/P2 | Docente recién registrado inicia sesión → rol='docente'"""
        resp = client.post("/auth/login", json={
            "correo":    _DOCENTE_HU["correo"],
            "contraseña": _DOCENTE_HU["contraseña"],
        })
        assert resp.status_code == 200
        assert resp.json()["rol"] == "docente"

    def test_HU02_paso3_docente_crea_curso(self, client):
        """HU-02/P3 | Docente crea un curso → 201 y el curso queda disponible"""
        resp = client.post("/cursos/", json={
            "nombre": "Historia de Colombia",
            "cupo_estudiante": 15,
            "horario": [{"dia": "Miercoles", "hora": "09:00"}],
            "id_docente": _hu["id_docente"],
            "estado": True,
        })
        assert resp.status_code == 201
        _hu["id_curso"] = resp.json()["id_curso"]

    def test_HU02_paso4_curso_aparece_en_listado_del_docente(self, client):
        """HU-02/P4 | El curso creado aparece al consultar cursos del docente"""
        resp = client.get(f"/cursos/por-docente/{_hu['id_docente']}")
        assert resp.status_code == 200
        ids = [c["id_curso"] for c in resp.json()]
        assert _hu["id_curso"] in ids


# === HU-03 | Un estudiante puede inscribirse en un curso disponible ===
class TestHU03EstudianteSeInscribeEnCurso:

    def test_HU03_paso1_inscribir_en_curso_disponible(self, client):
        """HU-03/P1 | Estudiante se inscribe en el curso → 201"""
        resp = client.post("/inscripciones/", json={
            "id_estudiante": _hu["id_estudiante"],
            "id_curso":      _hu["id_curso"],
        })
        assert resp.status_code == 201
        _hu["id_inscripcion"] = resp.json()["id"]

    def test_HU03_paso2_curso_aparece_en_horario_del_estudiante(self, client):
        """HU-03/P2 | El curso inscrito aparece en el horario del estudiante"""
        resp = client.get(f"/cursos/por-estudiante/{_hu['id_estudiante']}")
        assert resp.status_code == 200
        ids = [c["id_curso"] for c in resp.json()]
        assert _hu["id_curso"] in ids

    def test_HU03_paso3_no_puede_inscribirse_dos_veces(self, client):
        """HU-03/P3 | Intentar inscribirse al mismo curso nuevamente → 400"""
        resp = client.post("/inscripciones/", json={
            "id_estudiante": _hu["id_estudiante"],
            "id_curso":      _hu["id_curso"],
        })
        assert resp.status_code == 400


# === HU-04 | Un docente puede registrar y consultar calificaciones ===
class TestHU04DocenteRegistraCalificaciones:

    def test_HU04_paso1_docente_registra_nota_del_estudiante(self, client):
        """HU-04/P1 | Docente registra nota de parcial 1 para el estudiante → 201"""
        resp = client.post("/calificaciones/", json={
            "id_estudiante":  _hu["id_estudiante"],
            "id_curso":       _hu["id_curso"],
            "tipo_evaluacion": 1,
            "nota": 3.8,
        })
        assert resp.status_code == 201
        _hu["id_cal"] = resp.json()["id_calificacion"]

    def test_HU04_paso2_nota_fuera_de_rango_rechazada(self, client):
        """HU-04/P2 | Nota fuera del rango 0–5 no puede registrarse → 422"""
        resp = client.post("/calificaciones/", json={
            "id_estudiante":  _hu["id_estudiante"],
            "id_curso":       _hu["id_curso"],
            "tipo_evaluacion": 2,
            "nota": 7.0,
        })
        assert resp.status_code == 422

    def test_HU04_paso3_docente_puede_corregir_la_nota(self, client):
        """HU-04/P3 | Docente actualiza la nota registrada → 200 con nuevo valor"""
        resp = client.put(f"/calificaciones/{_hu['id_cal']}", json={"nota": 4.2})
        assert resp.status_code == 200
        assert float(resp.json()["nota"]) == 4.2

    def test_HU04_paso4_estudiante_tiene_promedio_calculado(self, client):
        """HU-04/P4 | Sistema calcula promedio del estudiante correctamente"""
        resp = client.get(f"/calificaciones/promedio-estudiante/{_hu['id_estudiante']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["promedio"] is not None
        assert 0.0 <= data["promedio"] <= 5.0
