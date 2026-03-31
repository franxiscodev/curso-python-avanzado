# [CLASE 4] conftest.py reorganizado: fixtures compartidas con pytest-mock.
# Antes (Clase 3): cada test construia su propio mock_client con unittest.mock + patch.
# Aqui: mock_httpx_weather y mock_httpx_route son fixtures reutilizables que usan
# mocker.patch() — mas consistente con la filosofia de pytest donde todo es fixture.
# [CLASE 5 ->] Se añadiran fixtures para httpx.AsyncClient cuando migremos a async.

"""Fixtures base compartidas por toda la suite de tests de PyCommute."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def weather_data() -> dict:
    """JSON de OpenWeather pregrabado."""
    return json.loads((FIXTURES_DIR / "weather_valencia.json").read_text())


@pytest.fixture
def route_data() -> dict:
    """JSON de OpenRouteService pregrabado."""
    return json.loads((FIXTURES_DIR / "route_valencia.json").read_text())


# [CLASE 4] mock_httpx_weather usa mocker.patch() de pytest-mock.
# Antes: cada test tenia su propio 'with patch("pycommute.weather.httpx.Client")'.
# Ahora: la fixture centraliza el mock — los tests solo la declaran como parametro.
@pytest.fixture
def mock_httpx_weather(mocker, weather_data: dict) -> MagicMock:
    """Mock de httpx.Client que devuelve weather_data sin llamada real.

    Usa pytest-mock (mocker.patch) para interceptar httpx.Client en el modulo
    weather. El mock se desmonta automaticamente al finalizar el test.

    Args:
        mocker: Fixture de pytest-mock.
        weather_data: JSON pregrabado de OpenWeather.

    Returns:
        Mock del cliente httpx ya configurado y parcheado.
    """
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = weather_data
    mock_response.raise_for_status.return_value = None
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response
    mocker.patch("pycommute.weather.httpx.Client", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_httpx_route(mocker, route_data: dict) -> MagicMock:
    """Mock de httpx.Client que devuelve route_data sin llamada real.

    Args:
        mocker: Fixture de pytest-mock.
        route_data: JSON pregrabado de OpenRouteService.

    Returns:
        Mock del cliente httpx ya configurado y parcheado.
    """
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = route_data
    mock_response.raise_for_status.return_value = None
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response
    mocker.patch("pycommute.route.httpx.Client", return_value=mock_client)
    return mock_client
