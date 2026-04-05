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
