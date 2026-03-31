# [CLASE 4] test_route.py expandido de 2 a 5 tests.
# Antes (Clase 2): 2 tests con unittest.mock + patch directo.
# Aqui: 5 tests usando la fixture mock_httpx_route de conftest.py.
# Nuevo en Clase 4:
#   - test_get_route_converts_units_correctly: verifica logica de conversion m->km, s->min
#   - test_get_route_preserves_profile: verifica que el perfil se preserva en el resultado
#   - test_get_route_accepts_valid_profiles: parametrize con 3 perfiles
# [CLASE 5 ->] Se añadiran tests async cuando migremos a httpx.AsyncClient.

"""Tests unitarios para pycommute.route."""

from unittest.mock import MagicMock

import httpx
import pytest

from pycommute.route import get_route

VALENCIA = (39.4697, -0.3763)
DESTINATION = (39.4870, -0.3560)


def test_get_route_returns_expected_fields(mock_httpx_route: MagicMock) -> None:
    """Verifica que get_route devuelve las keys correctas."""
    result = get_route(VALENCIA, DESTINATION, "cycling-regular", "fake-key")

    assert "distance_km" in result
    assert "duration_min" in result
    assert "profile" in result


# [CLASE 4] Nuevo: verificar la logica de conversion de unidades.
# El fixture route_valencia.json tiene distance=3200.5m y duration=720.3s.
# Este test documenta el contrato: metros -> km (1 decimal), segundos -> minutos (entero).
def test_get_route_converts_units_correctly(mock_httpx_route: MagicMock) -> None:
    """Verifica la conversion de unidades: metros a km, segundos a minutos.

    El fixture route_valencia.json tiene distance=3200.5m y duration=720.3s,
    que deben convertirse a 3.2 km y 12 min.
    """
    result = get_route(VALENCIA, DESTINATION, "cycling-regular", "fake-key")

    assert result["distance_km"] == 3.2
    assert result["duration_min"] == 12


# [CLASE 4] Nuevo: el perfil de transporte se pasa como argumento y debe preservarse.
# Este test verifica que get_route no ignora ni transforma el perfil recibido.
def test_get_route_preserves_profile(mock_httpx_route: MagicMock) -> None:
    """Verifica que el perfil de ruta se preserva en el resultado."""
    result = get_route(VALENCIA, DESTINATION, "driving-car", "fake-key")

    assert result["profile"] == "driving-car"


def test_get_route_raises_on_bad_key(mocker) -> None:
    """Verifica que HTTPStatusError se propaga con una API key invalida (403)."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "403 Forbidden",
        request=MagicMock(),
        response=MagicMock(status_code=403),
    )
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response
    mocker.patch("pycommute.route.httpx.Client", return_value=mock_client)

    with pytest.raises(httpx.HTTPStatusError):
        get_route(VALENCIA, DESTINATION, "cycling-regular", "key-invalida")


# [CLASE 4] Nuevo: parametrize con los 3 perfiles soportados por ORS.
# Cada perfil es un test independiente — si "driving-car" falla, los otros 2 siguen.
@pytest.mark.parametrize("profile", [
    "cycling-regular",
    "driving-car",
    "foot-walking",
])
def test_get_route_accepts_valid_profiles(
    mock_httpx_route: MagicMock, profile: str
) -> None:
    """Verifica que get_route acepta distintos perfiles y los preserva."""
    result = get_route(VALENCIA, DESTINATION, profile, "fake-key")

    assert result["profile"] == profile
