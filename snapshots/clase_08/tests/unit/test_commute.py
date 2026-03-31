"""Tests unitarios para pycommute.services.commute."""

from unittest.mock import AsyncMock

import pytest

from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.services.commute import CommuteService

WEATHER_RESULT = {"city": "Valencia", "temperature": 24.12, "description": "clear sky"}
ROUTE_RESULT = {"distance_km": 3.2, "duration_min": 12, "profile": "cycling-regular"}


def _make_service(route_result: dict | None = None) -> CommuteService:
    """Crea un CommuteService con adaptadores mockeados."""
    mock_weather = AsyncMock()
    mock_weather.get_current_weather = AsyncMock(return_value=WEATHER_RESULT)
    mock_route = AsyncMock()
    mock_route.get_route = AsyncMock(return_value=route_result or ROUTE_RESULT)
    return CommuteService(
        weather=mock_weather,
        route=mock_route,
        cache=MemoryCacheAdapter(),
    )


@pytest.mark.anyio
async def test_get_commute_info_returns_weather_and_routes() -> None:
    """Verifica que get_commute_info devuelve las keys weather y routes.

    Usa inyeccion de dependencias — los adaptadores se pasan por constructor.
    No se parchea httpx: ese nivel ya lo cubren test_weather.py y test_route.py.
    """
    service = _make_service()

    result = await service.get_commute_info(
        city="Valencia",
        destination_city="Madrid",
        profiles=["cycling-regular"],
        weather_key="fake-key",
        route_key="fake-key",
    )

    assert "weather" in result
    assert "routes" in result
    assert len(result["routes"]) == 1


@pytest.mark.anyio
async def test_get_commute_info_parallel_execution() -> None:
    """Verifica que se obtiene una ruta por cada perfil solicitado."""
    service = _make_service()

    result = await service.get_commute_info(
        city="Valencia",
        destination_city="Madrid",
        profiles=["cycling-regular", "driving-car"],
        weather_key="fake-key",
        route_key="fake-key",
    )

    assert len(result["routes"]) == 2
