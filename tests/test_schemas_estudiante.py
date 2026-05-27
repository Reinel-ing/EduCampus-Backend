"""
test_schemas_estudiante.py
Pruebas unitarias para schemas/estudiante.py
Cubre: EstudianteCreate, EstudianteUpdate — validaciones Pydantic
Técnicas: CE, VL, CB
"""
import pytest
from pydantic import ValidationError
from schemas.estudiante import EstudianteCreate, EstudianteUpdate


# Datos base válidos
ESTUDIANTE_VALIDO = {
    "nombres":    "Ana Martinez",
    "apellidos":  "Lopez Garcia",
    "cedula":     "1020304050",
    "correo":     "ana@gmail.com",
    "contraseña": "clave123",
    "telefono":   "3001234567",
    "estado":     True,
}


# === CLASES DE EQUIVALENCIA — campo correo ===
class TestCorreoEstudiante:

    def test_CE01_correo_gmail_valido(self):
        """CE-01 | correo @gmail.com → aceptado"""
        datos = {**ESTUDIANTE_VALIDO, "correo": "ana@gmail.com"}
        est = EstudianteCreate(**datos)
        assert est.correo == "ana@gmail.com"

    def test_CE02_correo_outlook_valido(self):
        """CE-02 | correo @outlook.com → aceptado"""
        datos = {**ESTUDIANTE_VALIDO, "correo": "ana@outlook.com"}
        est = EstudianteCreate(**datos)
        assert est.correo == "ana@outlook.com"

    def test_CE03_correo_yahoo_invalido(self):
        """CE-03 | correo @yahoo.com → ValidationError"""
        datos = {**ESTUDIANTE_VALIDO, "correo": "ana@yahoo.com"}
        with pytest.raises(ValidationError):
            EstudianteCreate(**datos)

    def test_CE04_correo_hotmail_invalido(self):
        """CE-04 | correo @hotmail.com → ValidationError"""
        datos = {**ESTUDIANTE_VALIDO, "correo": "ana@hotmail.com"}
        with pytest.raises(ValidationError):
            EstudianteCreate(**datos)

    def test_CE05_correo_sin_arroba_invalido(self):
        """CE-05 | correo sin @ → ValidationError"""
        datos = {**ESTUDIANTE_VALIDO, "correo": "anagmail.com"}
        with pytest.raises(ValidationError):
            EstudianteCreate(**datos)

    def test_CE06_correo_vacio_invalido(self):
        """CE-06 | correo vacío → ValidationError"""
        datos = {**ESTUDIANTE_VALIDO, "correo": ""}
        with pytest.raises(ValidationError):
            EstudianteCreate(**datos)


# === VALORES LÍMITE — campo correo ===
class TestCorreoLimites:

    def test_VL01_correo_normalizado_a_minusculas(self):
        """VL-01 | correo en mayúsculas → se normaliza a minúsculas"""
        datos = {**ESTUDIANTE_VALIDO, "correo": "ANA@GMAIL.COM"}
        est = EstudianteCreate(**datos)
        assert est.correo == "ana@gmail.com"

    def test_VL02_correo_minimo_gmail(self):
        """VL-02 | correo mínimo válido: 'a@gmail.com' → aceptado"""
        datos = {**ESTUDIANTE_VALIDO, "correo": "a@gmail.com"}
        est = EstudianteCreate(**datos)
        assert "gmail.com" in est.correo

    def test_VL03_correo_subdominio_invalido(self):
        """VL-03 | correo @mail.gmail.com (subdominio) → ValidationError"""
        datos = {**ESTUDIANTE_VALIDO, "correo": "ana@mail.gmail.com"}
        with pytest.raises(ValidationError):
            EstudianteCreate(**datos)


# === CAMINO BÁSICO — EstudianteCreate ===
class TestCaminoBasicoEstudiante:

    def test_CB01_camino_feliz_todos_validos(self):
        """CB-01 | todos los campos válidos → objeto creado sin errores"""
        est = EstudianteCreate(**ESTUDIANTE_VALIDO)
        assert est.nombres == "Ana Martinez"
        assert est.correo == "ana@gmail.com"
        assert est.estado is True

    def test_CB02_correo_invalido_lanza_validation_error(self):
        """CB-02 | correo inválido → ValidationError con mensaje descriptivo"""
        datos = {**ESTUDIANTE_VALIDO, "correo": "ana@otro.com"}
        with pytest.raises(ValidationError) as exc:
            EstudianteCreate(**datos)
        assert "gmail" in str(exc.value).lower() or "outlook" in str(exc.value).lower()

    def test_CB03_update_correo_none_no_valida(self):
        """CB-03 | EstudianteUpdate con correo=None → no lanza error"""
        upd = EstudianteUpdate(correo=None)
        assert upd.correo is None

    def test_CB04_update_correo_valido(self):
        """CB-04 | EstudianteUpdate con correo válido → aceptado"""
        upd = EstudianteUpdate(correo="nuevo@outlook.com")
        assert upd.correo == "nuevo@outlook.com"

    def test_CB05_update_correo_invalido_lanza_error(self):
        """CB-05 | EstudianteUpdate con correo inválido → ValidationError"""
        with pytest.raises(ValidationError):
            EstudianteUpdate(correo="nuevo@yahoo.com")
