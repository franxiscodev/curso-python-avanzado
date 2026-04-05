"""@pytest.mark.parametrize: un test, seis casos independientes.

Demuestra parametrize con 6 casos para evaluate_delay():
- Valores normales: 5 (OK), 30 (WARNING), 90 (DANGER)
- Edge cases de limite: 14 (ultimo OK), 15 (primer WARNING), 45 (primer DANGER)

Los 4 edge cases de limite son los mas importantes: si alguien cambia
un '<' por '<=' en evaluate_delay(), exactamente esos tests fallan.

Cada caso genera un test independiente con su propio ID en el reporte.
Si el caso [14-OK] falla, los otros 5 siguen ejecutando.

Ejecutar (desde curso/):
    uv run pytest scripts/clase_04/conceptos/03_pytest_parametrize.py -v
"""

import pytest


def evaluate_delay(minutes: int) -> str:
    if minutes < 15:
        return "OK"
    elif minutes < 45:
        return "WARNING"
    return "DANGER"


@pytest.mark.parametrize(
    "mins, expected_status",
    [
        (5,  "OK"),       # Caso de uso normal
        (14, "OK"),       # Edge case inferior
        (15, "WARNING"),  # Edge case límite
        (30, "WARNING"),  # Caso medio
        (45, "DANGER"),   # Límite superior
        (90, "DANGER"),   # Caso extremo
    ]
)
def test_evaluate_delay_all_cases(mins: int, expected_status: str):
    assert evaluate_delay(mins) == expected_status
