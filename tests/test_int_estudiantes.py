"""
test_int_estudiantes.py
Pruebas de integración para el endpoint /estudiantes/
Cubre operaciones CRUD completas con peticiones HTTP reales sobre SQLite.
Técnicas: Clases de Equivalencia (CE), Valores Límite (VL), Camino Básico (CB)
"""
import pytest

# ─── Datos de prueba únicos para esta suite ──────────────────────────────────
_ESTUDIANTE = {
    "nombres": "María",
    "apellidos": "Torres",
    "cedula": "10010010",
    "correo": "maria.torres.int@gmail.com",
    "contraseña": "Clave2024#",
    "telefono": "3102345678",
    "estado": True,
}

_id_est = None   # ID asignado tras la creación; usado en pruebas siguientes


class TestEstudiantesIntegracion:

    # ── Clases de Equivalencia ──────────────────────────────────────────────

    def test_CE01_crear_estudiante_valido_retorna_201(self, client):
        """CE-01 | POST /estudiantes/ con datos válidos → 201 y devuelve id_estudiante"""
        global _id_est
        resp = client.post("/estudiantes/", json=_ESTUDIANTE)
        assert resp.status_code == 201
        data = resp.json()
        assert "id_estudiante" in data
        assert data["correo"] == _ESTUDIANTE["correo"].lower()
        _id_est = data["id_estudiante"]

    def test_CE02_correo_dominio_invalido_retorna_422(self, client):
        """CE-02 | correo @yahoo.com → 422 (dominio no permitido por el validador)"""
        payload = {**_ESTUDIANTE, "cedula": "10010011", "correo": "prueba@yahoo.com"}
        resp = client.post("/estudiantes/", json=payload)
        assert resp.status_code == 422

    def test_CE03_listar_estudiantes_retorna_200_y_lista(self, client):
        """CE-03 | GET /estudiantes/ → 200 y la lista contiene al menos un registro"""
        resp = client.get("/estudiantes/")
        assert resp.status_code == 200
        datos = resp.json()
        assert isinstance(datos, list)
        assert len(datos) >= 1

    def test_CE04_obtener_por_id_existente_retorna_200(self, client):
        """CE-04 | GET /estudiantes/{id} con ID válido → 200 y datos correctos"""
        resp = client.get(f"/estudiantes/{_id_est}")
        assert resp.status_code == 200
        assert resp.json()["id_estudiante"] == _id_est

    def test_CE05_obtener_id_inexistente_retorna_404(self, client):
        """CE-05 | GET /estudiantes/999999 (no existe) → 404"""
        resp = client.get("/estudiantes/999999")
        assert resp.status_code == 404

    # ── Valores Límite ──────────────────────────────────────────────────────

    def test_VL01_correo_outlook_tambien_valido(self, client):
        """VL-01 | correo @outlook.com → 201 (segundo dominio permitido)"""
        payload = {
            **_ESTUDIANTE,
            "cedula": "10010012",
            "correo": "vl.outlook.test@outlook.com",
        }
        resp = client.post("/estudiantes/", json=payload)
        assert resp.status_code == 201
        nuevo_id = resp.json()["id_estudiante"]
        # Limpieza: eliminar el registro temporal
        client.delete(f"/estudiantes/{nuevo_id}")

    def test_VL02_actualizar_id_inexistente_retorna_404(self, client):
        """VL-02 | PUT /estudiantes/999999 → 404"""
        resp = client.put("/estudiantes/999999", json={"nombres": "Nadie"})
        assert resp.status_code == 404

    def test_VL03_eliminar_id_inexistente_retorna_404(self, client):
        """VL-03 | DELETE /estudiantes/999999 → 404"""
        resp = client.delete("/estudiantes/999999")
        assert resp.status_code == 404

    # ── Camino Básico ───────────────────────────────────────────────────────

    def test_CB01_actualizar_nombre_estudiante(self, client):
        """CB-01 | PUT /estudiantes/{id} → cambia nombres → 200 con datos actualizados"""
        resp = client.put(f"/estudiantes/{_id_est}", json={"nombres": "MariaEditada"})
        assert resp.status_code == 200
        assert resp.json()["nombres"] == "MariaEditada"

    def test_CB02_eliminar_estudiante_existente(self, client):
        """CB-02 | DELETE /estudiantes/{id} → 204 No Content"""
        resp = client.delete(f"/estudiantes/{_id_est}")
        assert resp.status_code == 204

    def test_CB03_obtener_estudiante_eliminado_retorna_404(self, client):
        """CB-03 | GET /estudiantes/{id} después de DELETE → 404 (ya no existe)"""
        resp = client.get(f"/estudiantes/{_id_est}")
        assert resp.status_code == 404
