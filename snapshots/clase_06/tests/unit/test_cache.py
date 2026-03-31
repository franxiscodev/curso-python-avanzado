"""Tests unitarios para pycommute.cache."""

import pytest

from pycommute.cache import get_coordinates


def test_get_coordinates_returns_correct_values() -> None:
    """Verifica que las coordenadas de Valencia son correctas."""
    lat, lon = get_coordinates("Valencia")

    assert abs(lat - 39.4699) < 0.001
    assert abs(lon - (-0.3763)) < 0.001


def test_get_coordinates_uses_cache() -> None:
    """Verifica que la segunda llamada es un cache hit."""
    get_coordinates.cache_clear()

    get_coordinates("Madrid")
    get_coordinates("Madrid")

    info = get_coordinates.cache_info()
    assert info.hits >= 1
    assert info.misses == 1


def test_get_coordinates_raises_for_unknown_city() -> None:
    """Verifica que una ciudad desconocida lanza ValueError."""
    with pytest.raises(ValueError, match="Ciudad no encontrada"):
        get_coordinates("CiudadInventada")
