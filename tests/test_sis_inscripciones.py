"""
test_sis_inscripciones.py
Pruebas de sistema para el módulo de inscripciones.
Verifica reglas de negocio: control de cupo, inscripciones duplicadas y
comportamiento ante datos inválidos, a través de peticiones HTTP reales.
Técnicas: Clases de Equivalencia (CE), Valores Límite (VL), Camino Básico (CB)
"""
import pytest

# ─── Datos únicos para esta suite ────────────────────────────────────────────
_DOCENTE_INS = {
    "nombres": "Jorge",
    "apellidos": "Castillo",
    "cedula": "50050050",
    "correo": "jorge.castillo.sis@gmail.com",
    "contraseña": "DocSis2024!",
    "especialidad": "Biología",
    "estado": True,
}

_ESTUDIANTE_A = {
    "nombres": "Pedro",
    "apellidos": "Bermudez",
    "cedula": "50050051",
    "correo": "pedro.bermudez.sis@gmail.com",
    "contraseña": "EstSisA2024!",
    "estado": True,
}

_ESTUDIANTE_B = {
    "nombres": "Luisa",
    "apellidos": "Herrera",
    "cedula": "50050052",
    "correo": "luisa.herrera.sis@gmail.com",
    "contraseña": "EstSisB2024!",
    "estado": True,
}

_sis_ins = {}   # IDs compartidos entre pasos del escenario


class TestSistemaInscripciones:

    # ── Preparación del escenario ─────────────────────────────────────────

    def test_SETUP01_crear_docente_y_curso_con_cupo_dos(self, client):
        """SETUP-01 | Crear docente y curso con cupo=2 como punto de partida"""
        resp_doc = client.post("/docentes/", json=_DOCENTE_INS)
        assert resp_doc.status_code == 201
        _sis_ins["id_docente"] = resp_doc.json()["id_docente"]

        resp_cur = client.post("/cursos/", json={
            "nombre": "Biología Celular",
            "cupo_estudiante": 2,
            "horario": [{"dia": "Jueves", "hora": "10:00"}],
            "id_docente": _sis_ins["id_docente"],
            "estado": True,
        })
        assert resp_cur.status_code == 201
        _sis_ins["id_curso"] = resp_cur.json()["id_curso"]

    def test_SETUP02_crear_dos_estudiantes(self, client):
        """SETUP-02 | Crear los dos estudiantes que se inscribirán"""
        resp_a = client.post("/estudiantes/", json=_ESTUDIANTE_A)
        assert resp_a.status_code == 201
        _sis_ins["id_est_a"] = resp_a.json()["id_estudiante"]

        resp_b = client.post("/estudiantes/", json=_ESTUDIANTE_B)
        assert resp_b.status_code == 201
        _sis_ins["id_est_b"] = resp_b.json()["id_estudiante"]

    # ── Clases de Equivalencia ────────────────────────────────────────────

    def test_CE01_inscribir_primer_estudiante(self, client):
        """CE-01 | Primera inscripción válida → 201"""
        resp = client.post("/inscripciones/", json={
            "id_estudiante": _sis_ins["id_est_a"],
            "id_curso":      _sis_ins["id_curso"],
        })
        assert resp.status_code == 201
        _sis_ins["id_ins_a"] = resp.json()["id"]

    def test_CE02_inscribir_segundo_estudiante(self, client):
        """CE-02 | Segunda inscripción (cupo aún disponible) → 201"""
        resp = client.post("/inscripciones/", json={
            "id_estudiante": _sis_ins["id_est_b"],
            "id_curso":      _sis_ins["id_curso"],
        })
        assert resp.status_code == 201

    def test_CE03_cupo_lleno_rechaza_nueva_inscripcion(self, client):
        """CE-03 | Cupo=2 ya completo → 400 al intentar inscribir un 3er estudiante"""
        # Crear un estudiante extra
        resp_c = client.post("/estudiantes/", json={
            "nombres": "Roberto",
            "apellidos": "Mora",
            "cedula": "50050053",
            "correo": "roberto.mora.sis@gmail.com",
            "contraseña": "EstSisC2024!",
            "estado": True,
        })
        assert resp_c.status_code == 201
        id_est_c = resp_c.json()["id_estudiante"]

        resp = client.post("/inscripciones/", json={
            "id_estudiante": id_est_c,
            "id_curso":      _sis_ins["id_curso"],
        })
        assert resp.status_code == 400
        assert "cupo" in resp.json()["detail"].lower()

    def test_CE04_inscripcion_duplicada_rechazada(self, client):
        """CE-04 | Intentar inscribir al mismo estudiante dos veces → 400"""
        resp = client.post("/inscripciones/", json={
            "id_estudiante": _sis_ins["id_est_a"],
            "id_curso":      _sis_ins["id_curso"],
        })
        assert resp.status_code == 400
        assert "inscrito" in resp.json()["detail"].lower()

    def test_CE05_inscripcion_en_curso_inexistente_retorna_404(self, client):
        """CE-05 | id_curso que no existe → 404"""
        resp = client.post("/inscripciones/", json={
            "id_estudiante": _sis_ins["id_est_a"],
            "id_curso":      999999,
        })
        assert resp.status_code == 404

    # ── Valores Límite ────────────────────────────────────────────────────

    def test_VL01_inscripcion_con_estudiante_inexistente_retorna_404(self, client):
        """VL-01 | id_estudiante que no existe → 404"""
        resp = client.post("/inscripciones/", json={
            "id_estudiante": 999999,
            "id_curso":      _sis_ins["id_curso"],
        })
        assert resp.status_code == 404

    def test_VL02_verificar_cupo_disponible_es_cero(self, client):
        """VL-02 | GET /cursos/{id}/verificar-cupo con cupo lleno → disponible=0"""
        resp = client.get(f"/cursos/{_sis_ins['id_curso']}/verificar-cupo")
        assert resp.status_code == 200
        data = resp.json()
        assert data["cupo"]       == 2
        assert data["inscritos"]  == 2
        assert data["disponible"] == 0

    # ── Camino Básico ─────────────────────────────────────────────────────

    def test_CB01_listar_inscritos_del_curso(self, client):
        """CB-01 | GET /inscripciones/por-curso/{id} → lista con 2 estudiantes"""
        resp = client.get(f"/inscripciones/por-curso/{_sis_ins['id_curso']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_CB02_listar_cursos_del_estudiante(self, client):
        """CB-02 | GET /inscripciones/por-estudiante/{id} → incluye el curso inscrito"""
        resp = client.get(f"/inscripciones/por-estudiante/{_sis_ins['id_est_a']}")
        assert resp.status_code == 200
        assert _sis_ins["id_curso"] in resp.json()

    def test_CB03_cancelar_inscripcion_libera_cupo(self, client):
        """CB-03 | DELETE /inscripciones/{id} → el cupo disponible sube de 0 a 1"""
        client.delete(f"/inscripciones/{_sis_ins['id_ins_a']}")

        resp = client.get(f"/cursos/{_sis_ins['id_curso']}/verificar-cupo")
        assert resp.status_code == 200
        data = resp.json()
        assert data["inscritos"]  == 1
        assert data["disponible"] == 1
