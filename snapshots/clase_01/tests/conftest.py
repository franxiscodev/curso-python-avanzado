# [CLASE 1] Fixtures base mínimas: una sola fixture que carga el JSON pregrabado.
# [CLASE 4 →] Se añadirán fixtures más complejas: mocks parametrizados,
# helpers de construcción de datos y gestión del ciclo de vida de recursos.

"""Fixtures base compartidas por toda la suite de tests de PyCommute."""

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def weather_valencia_json() -> dict:
    """Carga la respuesta pregrabada de OpenWeather para Valencia.

    Returns:
        Diccionario con la respuesta real de la API (cod 200, Valencia ES).
    """
    with open(FIXTURES_DIR / "weather_valencia.json") as f:
        return json.load(f)
