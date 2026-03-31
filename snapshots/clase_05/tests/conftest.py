# [CLASE 5] conftest.py actualizado: mocks migrados de MagicMock a AsyncMock.
# Antes (Clase 4): mock_httpx_weather/mock_httpx_route con httpx.Client (sincrono).
# Aqui: AsyncMock para httpx.AsyncClient — __aenter__, __aexit__ y get son async.
# Nota tecnica: no usamos spec=httpx.AsyncClient porque ambas fixtures parchean
# el mismo atributo httpx.AsyncClient (mismo modulo) y el segundo spec fallaria.
# [CLASE 6 ->] Sin cambios previstos en las fixtures de base.
"""Fixtures base compartidas por toda la suite de tests de PyCommute."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

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


@pytest.fixture
def mock_httpx_weather(mocker, weather_data: dict) -> AsyncMock:
    """Mock de httpx.AsyncClient que devuelve weather_data sin llamada real.

    Usa pytest-mock (mocker.patch) para interceptar httpx.AsyncClient en el
    módulo weather. El mock se desmonta automáticamente al finalizar el test.

    Args:
        mocker: Fixture de pytest-mock.
        weather_data: JSON pregrabado de OpenWeather.

    Returns:
        Mock async del cliente httpx ya configurado y parcheado.
    """
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = weather_data
    mock_response.raise_for_status.return_value = None
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    mocker.patch("pycommute.weather.httpx.AsyncClient", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_httpx_route(mocker, route_data: dict) -> AsyncMock:
    """Mock de httpx.AsyncClient que devuelve route_data sin llamada real.

    Args:
        mocker: Fixture de pytest-mock.
        route_data: JSON pregrabado de OpenRouteService.

    Returns:
        Mock async del cliente httpx ya configurado y parcheado.
    """
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = route_data
    mock_response.raise_for_status.return_value = None
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    mocker.patch("pycommute.route.httpx.AsyncClient", return_value=mock_client)
    return mock_client
