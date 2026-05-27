"""
test_schemas_calificacion.py
Pruebas unitarias para schemas/calificacion.py
Cubre: CalificacionCreate — campo nota (escala 0.0–5.0)
Técnicas: CE, VL, CB
"""
import pytest
from pydantic import ValidationError
from schemas.calificacion import CalificacionCreate, CalificacionUpdate


CALIFICACION_VALIDA = {
    "id_estudiante":   1,
    "id_curso":        1,
    "tipo_evaluacion": 1,
    "nota":            3.5,
}


# === CLASES DE EQUIVALENCIA — campo nota ===
class TestNotaCalificacion:

    def test_CE01_nota_dentro_del_rango_valida(self):
        """CE-01 | nota=3.5 (dentro de 0-5) → objeto creado"""
        cal = CalificacionCreate(**CALIFICACION_VALIDA)
        assert cal.nota == 3.5

    def test_CE02_nota_cero_valida(self):
        """CE-02 | nota=0.0 (límite inferior) → válida"""
        cal = CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": 0.0})
        assert cal.nota == 0.0

    def test_CE03_nota_cinco_valida(self):
        """CE-03 | nota=5.0 (límite superior) → válida"""
        cal = CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": 5.0})
        assert cal.nota == 5.0

    def test_CE04_nota_negativa_invalida(self):
        """CE-04 | nota=-1.0 → debe ser INVALIDA (fuera de escala 0-5)"""
        with pytest.raises(ValidationError):
            CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": -1.0})

    def test_CE05_nota_mayor_cinco_invalida(self):
        """CE-05 | nota=6.0 → debe ser INVALIDA (fuera de escala 0-5)"""
        with pytest.raises(ValidationError):
            CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": 6.0})


# === VALORES LÍMITE — nota (límite: 0.0 a 5.0) ===
class TestNotaLimites:

    def test_VL01_nota_menos_0_1_invalida(self):
        """VL-01 | nota=-0.1 (justo debajo del mínimo) → INVALIDA"""
        with pytest.raises(ValidationError):
            CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": -0.1})

    def test_VL02_nota_exactamente_0_valida(self):
        """VL-02 | nota=0.0 (exactamente el mínimo) → válida"""
        cal = CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": 0.0})
        assert cal.nota == 0.0

    def test_VL03_nota_exactamente_5_valida(self):
        """VL-03 | nota=5.0 (exactamente el máximo) → válida"""
        cal = CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": 5.0})
        assert cal.nota == 5.0

    def test_VL04_nota_5_1_invalida(self):
        """VL-04 | nota=5.1 (justo sobre el máximo) → INVALIDA"""
        with pytest.raises(ValidationError):
            CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": 5.1})

    def test_VL05_nota_0_1_valida(self):
        """VL-05 | nota=0.1 (justo sobre el mínimo) → válida"""
        cal = CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": 0.1})
        assert cal.nota == pytest.approx(0.1)

    def test_VL06_nota_4_9_valida(self):
        """VL-06 | nota=4.9 (justo bajo el máximo) → válida"""
        cal = CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": 4.9})
        assert cal.nota == pytest.approx(4.9)


# === CAMINO BÁSICO — CalificacionCreate ===
class TestCaminoBasicoCalificacion:

    def test_CB01_camino_feliz_todos_validos(self):
        """CB-01 | todos los campos válidos → objeto creado sin errores"""
        cal = CalificacionCreate(**CALIFICACION_VALIDA)
        assert cal.id_estudiante == 1
        assert cal.id_curso == 1
        assert cal.nota == 3.5

    def test_CB02_nota_entero_se_acepta_como_float(self):
        """CB-02 | nota=4 (int) → se convierte a 4.0 (float) correctamente"""
        cal = CalificacionCreate(**{**CALIFICACION_VALIDA, "nota": 4})
        assert cal.nota == 4.0
        assert isinstance(cal.nota, float)

    def test_CB03_update_nota_none_permitido(self):
        """CB-03 | CalificacionUpdate nota=None → acepta (campo opcional)"""
        upd = CalificacionUpdate(nota=None)
        assert upd.nota is None

    def test_CB04_update_nota_valida(self):
        """CB-04 | CalificacionUpdate nota=2.5 → aceptada"""
        upd = CalificacionUpdate(nota=2.5)
        assert upd.nota == 2.5
