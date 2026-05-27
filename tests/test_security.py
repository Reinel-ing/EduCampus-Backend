"""
test_security.py
Pruebas unitarias para utils/security.py
Cubre: hash_password y verify_password
Técnicas: Clases de Equivalencia (CE), Valores Límite (VL), Camino Básico (CB)
"""
import pytest
from utils.security import hash_password, verify_password


# === CLASES DE EQUIVALENCIA — hash_password ===
class TestHashPassword:

    def test_CE01_contrasena_valida_retorna_string(self):
        """CE-01 | contraseña válida → retorna un string no vacío"""
        resultado = hash_password("clave123")
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_CE02_hash_diferente_al_original(self):
        """CE-02 | el hash NO debe ser igual a la contraseña original"""
        original = "clave123"
        resultado = hash_password(original)
        assert resultado != original

    def test_CE03_contrasena_especial_hashea_sin_error(self):
        """CE-03 | contraseña con caracteres especiales → hashea sin error"""
        resultado = hash_password("C@av3#$%&/()=")
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_CE04_contrasena_espacios_hashea_sin_error(self):
        """CE-04 | contraseña con espacios → hashea sin error"""
        resultado = hash_password("mi clave secreta")
        assert isinstance(resultado, str)


# === CLASES DE EQUIVALENCIA — verify_password ===
class TestVerifyPassword:

    def test_CE05_contrasena_correcta_retorna_true(self):
        """CE-05 | contraseña correcta contra su hash → True"""
        hashed = hash_password("clave123")
        assert verify_password("clave123", hashed) is True

    def test_CE06_contrasena_incorrecta_retorna_false(self):
        """CE-06 | contraseña incorrecta → False"""
        hashed = hash_password("clave123")
        assert verify_password("otraClaveWrong", hashed) is False

    def test_CE07_contrasena_vacia_contra_hash_retorna_false(self):
        """CE-07 | contraseña vacía contra hash válido → False"""
        hashed = hash_password("clave123")
        assert verify_password("", hashed) is False

    def test_CE08_hash_malformado_retorna_false(self):
        """CE-08 | hash malformado → no lanza excepción, retorna False"""
        resultado = verify_password("clave123", "esto_no_es_un_hash_valido")
        assert resultado is False

    def test_CE09_hash_vacio_retorna_false(self):
        """CE-09 | hash vacío → retorna False sin excepción"""
        resultado = verify_password("clave123", "")
        assert resultado is False


# === VALORES LÍMITE — hash_password ===
class TestHashPasswordLimites:

    def test_VL01_contrasena_un_caracter(self):
        """VL-01 | contraseña de 1 carácter (mínimo posible) → funciona"""
        resultado = hash_password("a")
        assert isinstance(resultado, str) and len(resultado) > 0

    def test_VL02_contrasena_72_caracteres_limite_bcrypt(self):
        """VL-02 | contraseña de 72 caracteres (límite interno de bcrypt) → funciona"""
        contrasena = "A" * 72
        resultado = hash_password(contrasena)
        assert isinstance(resultado, str) and len(resultado) > 0

    def test_VL03_contrasena_100_caracteres(self):
        """VL-03 | contraseña de 100 chars (sobre límite bcrypt 72) → trunca y hashea sin error"""
        # bcrypt tiene límite de 72 bytes; security.py trunca automáticamente
        contrasena = "B" * 100
        resultado = hash_password(contrasena)
        assert isinstance(resultado, str) and len(resultado) > 0


# === CAMINO BÁSICO — flujo completo ===
class TestFlujoCaminoBasico:

    def test_CB01_hash_y_verify_flujo_correcto(self):
        """CB-01 | camino feliz: hash → verify con misma contraseña → True"""
        contrasena = "miClaveSegura99"
        hashed = hash_password(contrasena)
        assert verify_password(contrasena, hashed) is True

    def test_CB02_hash_y_verify_flujo_incorrecto(self):
        """CB-02 | hash → verify con contraseña diferente → False"""
        hashed = hash_password("contraseñaReal")
        assert verify_password("contraseñaFalsa", hashed) is False

    def test_CB03_dos_hashes_de_misma_contrasena_son_distintos(self):
        """CB-03 | dos hashes de la misma contraseña deben ser DISTINTOS (salt aleatorio)"""
        h1 = hash_password("clave123")
        h2 = hash_password("clave123")
        assert h1 != h2

    def test_CB04_verify_es_case_sensitive(self):
        """CB-04 | verify distingue mayúsculas y minúsculas"""
        hashed = hash_password("Clave123")
        assert verify_password("clave123", hashed) is False
        assert verify_password("Clave123", hashed) is True
