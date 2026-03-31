# [CLASE 5] Nuevo: test_commute.py para el orquestador get_commute_info.
# Decision de diseno: mockear las funciones importadas (get_current_weather,
# get_route) en lugar de httpx. Razon: el orquestador no debe testearse
# a nivel HTTP — eso ya lo cubren test_weather.py y test_route.py.
# Si mockeamos httpx en ambas fixtures juntas, el segundo patch sobreescribe
# al primero (mismo modulo httpx). Mockear las funciones evita el conflicto.
# [CLASE 6 ->] Sin cambios previstos en este modulo de tests.
"""Tests unitarios para pycommute.commute."""

import pytest

from pycommute.commute import get_commute_info

VALENCIA = (39.4697, -0.3763)
DESTINATION = (39.4870, -0.3560)

WEATHER_RESULT = {"city": "Valencia", "temperature": 24.12, "description": "clear sky"}
ROUTE_RESULT = {"distance_km": 3.2, "duration_min": 12, "profile": "cycling-regular"}


@pytest.mark.anyio
async def test_get_commute_info_returns_weather_and_routes(mocker) -> None:
    """Verifica que get_commute_info devuelve las keys weather y routes.

    Mockea get_current_weather y get_route directamente — no httpx.
    El orquestador no debe testearse a nivel HTTP: ese nivel ya está
    cubierto por test_weather.py y test_route.py.
    """
    mocker.patch("pycommute.commute.get_current_weather", return_value=WEATHER_RESULT)
    mocker.patch("pycommute.commute.get_route", return_value=ROUTE_RESULT)

    result = await get_commute_info(
        city="Valencia",
        origin=VALENCIA,
        destination=DESTINATION,
        profiles=["cycling-regular"],
        weather_key="fake-key",
        route_key="fake-key",
    )

    assert "weather" in result
    assert "routes" in result
    assert len(result["routes"]) == 1


@pytest.mark.anyio
async def test_get_commute_info_parallel_execution(mocker) -> None:
    """Verifica que se obtiene una ruta por cada perfil solicitado."""
    mocker.patch("pycommute.commute.get_current_weather", return_value=WEATHER_RESULT)
    mocker.patch("pycommute.commute.get_route", return_value=ROUTE_RESULT)

    result = await get_commute_info(
        city="Valencia",
        origin=VALENCIA,
        destination=DESTINATION,
        profiles=["cycling-regular", "driving-car"],
        weather_key="fake-key",
        route_key="fake-key",
    )

    assert len(result["routes"]) == 2
