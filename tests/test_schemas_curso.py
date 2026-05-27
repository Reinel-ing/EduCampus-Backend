"""
test_schemas_curso.py
Pruebas unitarias para schemas/curso.py
Cubre: CursoCreate, CursoUpdate — campo cupo_estudiante y nombre
Técnicas: CE, VL, CB
"""
import pytest
from pydantic import ValidationError
from schemas.curso import CursoCreate, CursoUpdate


CURSO_VALIDO = {
    "nombre":          "Matematicas I",
    "cupo_estudiante": 30,
    "horario":         [{"dia": "Lunes", "hora": "08:00-10:00"}],
    "id_docente":      1,
    "estado":          True,
}


# === CLASES DE EQUIVALENCIA — campo cupo_estudiante ===
class TestCupoCurso:

    def test_CE01_cupo_positivo_valido(self):
        """CE-01 | cupo=30 → válido"""
        curso = CursoCreate(**CURSO_VALIDO)
        assert curso.cupo_estudiante == 30

    def test_CE02_cupo_cero_invalido(self):
        """CE-02 | cupo=0 → debe ser INVALIDO (mínimo 1 estudiante)"""
        with pytest.raises(ValidationError):
            CursoCreate(**{**CURSO_VALIDO, "cupo_estudiante": 0})

    def test_CE03_cupo_negativo_invalido(self):
        """CE-03 | cupo=-5 → debe ser INVALIDO"""
        with pytest.raises(ValidationError):
            CursoCreate(**{**CURSO_VALIDO, "cupo_estudiante": -5})

    def test_CE04_cupo_fraccionario_invalido(self):
        """CE-04 | cupo=15.5 → debe ser INVALIDO (debe ser entero)"""
        with pytest.raises((ValidationError, ValueError)):
            CursoCreate(**{**CURSO_VALIDO, "cupo_estudiante": 15.5})


# === VALORES LÍMITE — cupo_estudiante (límite mínimo: 1) ===
class TestCupoLimites:

    def test_VL01_cupo_cero_invalido(self):
        """VL-01 | cupo=0 (justo debajo del mínimo) → INVALIDO"""
        with pytest.raises(ValidationError):
            CursoCreate(**{**CURSO_VALIDO, "cupo_estudiante": 0})

    def test_VL02_cupo_uno_valido(self):
        """VL-02 | cupo=1 (exactamente el mínimo) → válido"""
        curso = CursoCreate(**{**CURSO_VALIDO, "cupo_estudiante": 1})
        assert curso.cupo_estudiante == 1

    def test_VL03_cupo_dos_valido(self):
        """VL-03 | cupo=2 (justo sobre el mínimo) → válido"""
        curso = CursoCreate(**{**CURSO_VALIDO, "cupo_estudiante": 2})
        assert curso.cupo_estudiante == 2


# === CLASES DE EQUIVALENCIA — campo horario ===
class TestHorarioCurso:

    def test_CE05_horario_lista_valida(self):
        """CE-05 | horario como lista con elementos → válido"""
        curso = CursoCreate(**CURSO_VALIDO)
        assert isinstance(curso.horario, list)
        assert len(curso.horario) > 0

    def test_CE06_horario_lista_vacia_invalida(self):
        """CE-06 | horario lista vacía → debe ser INVALIDO"""
        with pytest.raises(ValidationError):
            CursoCreate(**{**CURSO_VALIDO, "horario": []})

    def test_CE07_horario_multiples_dias_valido(self):
        """CE-07 | horario con múltiples días → válido"""
        horario = [
            {"dia": "Lunes",     "hora": "08:00-10:00"},
            {"dia": "Miercoles", "hora": "08:00-10:00"},
        ]
        curso = CursoCreate(**{**CURSO_VALIDO, "horario": horario})
        assert len(curso.horario) == 2


# === CAMINO BÁSICO — CursoCreate ===
class TestCaminoBasicoCurso:

    def test_CB01_camino_feliz_todos_validos(self):
        """CB-01 | todos los campos válidos → objeto creado sin errores"""
        curso = CursoCreate(**CURSO_VALIDO)
        assert curso.nombre == "Matematicas I"
        assert curso.cupo_estudiante == 30
        assert curso.estado is True

    def test_CB02_estado_por_defecto_true(self):
        """CB-02 | estado no especificado → por defecto True"""
        datos = {k: v for k, v in CURSO_VALIDO.items() if k != "estado"}
        curso = CursoCreate(**datos)
        assert curso.estado is True

    def test_CB03_update_cupo_none_permitido(self):
        """CB-03 | CursoUpdate cupo=None → acepta (campo opcional)"""
        upd = CursoUpdate(cupo_estudiante=None)
        assert upd.cupo_estudiante is None

    def test_CB04_update_cupo_valido(self):
        """CB-04 | CursoUpdate cupo=50 → aceptado"""
        upd = CursoUpdate(cupo_estudiante=50)
        assert upd.cupo_estudiante == 50
