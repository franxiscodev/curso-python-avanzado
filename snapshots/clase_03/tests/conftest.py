# [CLASE 3] Sin cambios respecto a Clase 2.
# [CLASE 4 →] Se añadirán fixtures para testear el comportamiento de @retry
# (mock de ConnectError, verificación de número de intentos) y Settings
# (monkeypatch de variables de entorno para tests de config.py).

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


@pytest.fixture
def route_valencia_json() -> dict:
    """Carga la respuesta pregrabada de OpenRouteService para Valencia.

    Returns:
        Diccionario con la respuesta real de la API (cycling-regular,
        ruta corta de ~3.2 km / 12 min en Valencia ES).
    """
    with open(FIXTURES_DIR / "route_valencia.json") as f:
        return json.load(f)
