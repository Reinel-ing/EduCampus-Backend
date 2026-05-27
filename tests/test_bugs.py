"""
test_bugs.py
Pruebas diseñadas para detectar fallos REALES en los schemas del backend.
Si un test falla aquí, hay un bug en el código que debe corregirse.
"""
import pytest
from pydantic import ValidationError
from utils.security import hash_password, verify_password
from schemas.calificacion import CalificacionCreate
from schemas.curso import CursoCreate


# === BUG-01 | verify_password con hash malformado → retorna False silenciosamente ===
class TestBug01VerifyPasswordSeguro:

    def test_hash_malformado_retorna_false_no_excepcion(self):
        """BUG-01 | hash no-bcrypt → no explota la app, retorna False"""
        # Si esto lanza excepción → bug: el endpoint de login colapsaría
        resultado = verify_password("cualquierClave", "no_soy_un_hash_bcrypt_$$$$")
        assert resultado is False

    def test_hash_sql_injection_no_explota(self):
        """BUG-01b | hash con caracteres SQL → no lanza excepción"""
        resultado = verify_password("clave", "' OR '1'='1'; DROP TABLE usuarios;--")
        assert resultado is False

    def test_hash_none_string_no_explota(self):
        """BUG-01c | hash='None' (string) → False, sin excepción"""
        resultado = verify_password("clave", "None")
        assert resultado is False


# === BUG-02 | CalificacionCreate: notas fuera del rango 0–5 deben ser INVÁLIDAS ===
class TestBug02NotaSinRango:

    def test_nota_negativa_debe_ser_invalida(self):
        """BUG-02a | nota=-1.0 debe ser INVALIDA → escala colombiana es 0.0–5.0"""
        with pytest.raises(ValidationError):
            CalificacionCreate(
                id_estudiante=1, id_curso=1,
                tipo_evaluacion=1, nota=-1.0
            )

    def test_nota_mayor_cinco_debe_ser_invalida(self):
        """BUG-02b | nota=10.0 debe ser INVALIDA → no existe nota > 5.0"""
        with pytest.raises(ValidationError):
            CalificacionCreate(
                id_estudiante=1, id_curso=1,
                tipo_evaluacion=1, nota=10.0
            )

    def test_nota_menos_0_1_debe_ser_invalida(self):
        """BUG-02c | nota=-0.1 (justo bajo el mínimo) → INVALIDA"""
        with pytest.raises(ValidationError):
            CalificacionCreate(
                id_estudiante=1, id_curso=1,
                tipo_evaluacion=1, nota=-0.1
            )


# === BUG-03 | CursoCreate: cupo=0 o negativo debe ser INVÁLIDO ===
class TestBug03CupoSinMinimo:

    def test_cupo_cero_debe_ser_invalido(self):
        """BUG-03a | cupo=0 debe ser INVALIDO → no existe curso sin estudiantes"""
        with pytest.raises(ValidationError):
            CursoCreate(
                nombre="Curso Vacío",
                cupo_estudiante=0,
                horario=[{"dia": "Lunes", "hora": "08:00"}],
                id_docente=1,
                estado=True
            )

    def test_cupo_negativo_debe_ser_invalido(self):
        """BUG-03b | cupo=-10 debe ser INVALIDO"""
        with pytest.raises(ValidationError):
            CursoCreate(
                nombre="Curso Negativo",
                cupo_estudiante=-10,
                horario=[{"dia": "Lunes", "hora": "08:00"}],
                id_docente=1,
                estado=True
            )
