"""
test_schemas_docente.py
Pruebas unitarias para schemas/docente.py
Cubre: DocenteCreate, DocenteUpdate — validaciones Pydantic
Técnicas: CE, VL, CB
"""
import pytest
from pydantic import ValidationError
from schemas.docente import DocenteCreate, DocenteUpdate


DOCENTE_VALIDO = {
    "nombres":      "Carlos Perez",
    "apellidos":    "Rodriguez Lima",
    "cedula":       "9876543210",
    "correo":       "carlos@gmail.com",
    "contraseña":   "clave123",
    "especialidad": "Matematicas",
    "estado":       True,
}


# === CLASES DE EQUIVALENCIA — campo correo ===
class TestCorreoDocente:

    def test_CE01_correo_gmail_valido(self):
        """CE-01 | correo @gmail.com → aceptado"""
        doc = DocenteCreate(**{**DOCENTE_VALIDO, "correo": "docente@gmail.com"})
        assert doc.correo == "docente@gmail.com"

    def test_CE02_correo_outlook_valido(self):
        """CE-02 | correo @outlook.com → aceptado"""
        doc = DocenteCreate(**{**DOCENTE_VALIDO, "correo": "docente@outlook.com"})
        assert doc.correo == "docente@outlook.com"

    def test_CE03_correo_dominio_no_permitido(self):
        """CE-03 | correo @hotmail.com → ValidationError"""
        with pytest.raises(ValidationError):
            DocenteCreate(**{**DOCENTE_VALIDO, "correo": "docente@hotmail.com"})

    def test_CE04_correo_sin_dominio(self):
        """CE-04 | correo sin dominio 'docente@' → ValidationError"""
        with pytest.raises(ValidationError):
            DocenteCreate(**{**DOCENTE_VALIDO, "correo": "docente@"})

    def test_CE05_correo_sin_arroba(self):
        """CE-05 | correo sin @ → ValidationError"""
        with pytest.raises(ValidationError):
            DocenteCreate(**{**DOCENTE_VALIDO, "correo": "docentegmail.com"})


# === VALORES LÍMITE — campo correo ===
class TestCorreoDocenteLimites:

    def test_VL01_correo_mayusculas_normalizado(self):
        """VL-01 | correo en MAYÚSCULAS → normalizado a minúsculas"""
        doc = DocenteCreate(**{**DOCENTE_VALIDO, "correo": "CARLOS@OUTLOOK.COM"})
        assert doc.correo == "carlos@outlook.com"

    def test_VL02_correo_mixto_normalizado(self):
        """VL-02 | correo mixto 'Carlos@Gmail.Com' → normalizado"""
        doc = DocenteCreate(**{**DOCENTE_VALIDO, "correo": "Carlos@Gmail.Com"})
        assert doc.correo == "carlos@gmail.com"


# === CAMINO BÁSICO — DocenteCreate ===
class TestCaminoBasicoDocente:

    def test_CB01_camino_feliz_todos_validos(self):
        """CB-01 | todos los campos válidos → objeto creado correctamente"""
        doc = DocenteCreate(**DOCENTE_VALIDO)
        assert doc.nombres == "Carlos Perez"
        assert doc.especialidad == "Matematicas"
        assert doc.estado is True

    def test_CB02_especialidad_opcional_puede_ser_none(self):
        """CB-02 | especialidad no es requerida → acepta None"""
        datos = {**DOCENTE_VALIDO, "especialidad": None}
        doc = DocenteCreate(**datos)
        assert doc.especialidad is None

    def test_CB03_correo_invalido_lanza_error_con_mensaje(self):
        """CB-03 | correo inválido → ValidationError con mensaje útil"""
        with pytest.raises(ValidationError) as exc:
            DocenteCreate(**{**DOCENTE_VALIDO, "correo": "x@otro.net"})
        assert "gmail" in str(exc.value).lower() or "outlook" in str(exc.value).lower()

    def test_CB04_update_correo_none_permitido(self):
        """CB-04 | DocenteUpdate correo=None → no valida, acepta"""
        upd = DocenteUpdate(correo=None)
        assert upd.correo is None

    def test_CB05_update_correo_invalido_rechazado(self):
        """CB-05 | DocenteUpdate correo inválido → ValidationError"""
        with pytest.raises(ValidationError):
            DocenteUpdate(correo="docente@yahoo.com")
