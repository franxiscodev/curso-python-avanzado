"""Tests unitarios para pycommute.core.models."""

import pytest
from pydantic import ValidationError

from pycommute.core.models import (
    CommuteResult,
    ConsultaEntry,
    RouteData,
    WeatherData,
)

WEATHER = WeatherData(temperature=22.0, description="clear sky", city="Valencia")
ROUTE_CYCLING = RouteData(distance_km=2.0, duration_min=8.0, profile="cycling-regular")
ROUTE_DRIVING = RouteData(distance_km=2.1, duration_min=5.0, profile="driving-car")


def test_weather_data_valid() -> None:
    """Verifica que WeatherData acepta datos validos y normaliza description."""
    w = WeatherData(temperature=13.5, description="Clear Sky", city="Valencia")

    assert w.temperature == 13.5
    assert w.description == "clear sky"  # normalizado a lowercase


def test_weather_data_invalid_temperature() -> None:
    """Verifica que temperatura fuera de rango lanza ValidationError."""
    with pytest.raises(ValidationError, match="Temperatura irrealista"):
        WeatherData(temperature=999.0, description="hot", city="Venus")


def test_route_data_invalid_profile() -> None:
    """Verifica que perfil no soportado lanza ValidationError."""
    with pytest.raises(ValidationError, match="Perfil invalido"):
        RouteData(distance_km=2.0, duration_min=8.0, profile="flying-car")


def test_commute_result_sets_best_route_automatically() -> None:
    """Verifica que CommuteResult calcula best_route en el model_validator."""
    result = CommuteResult(weather=WEATHER, routes=[ROUTE_CYCLING, ROUTE_DRIVING])

    assert result.best_route is not None
    assert result.best_route.profile == "driving-car"  # menor duration_min (5 < 8)


def test_consulta_entry_serializable() -> None:
    """Verifica que ConsultaEntry es serializable a dict con model_dump()."""
    result = CommuteResult(weather=WEATHER, routes=[ROUTE_CYCLING])
    entry = ConsultaEntry(city="Valencia", profiles=["cycling-regular"], result=result)

    data = entry.model_dump()

    assert "timestamp" in data
    assert "city" in data
    assert data["city"] == "Valencia"
    assert "result" in data
