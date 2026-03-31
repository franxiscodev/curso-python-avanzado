# [CLASE 4] test_weather.py expandido de 2 a 5 tests.
# Antes (Clase 3): 2 tests con unittest.mock + patch directo en cada funcion.
# Aqui: 5 tests usando la fixture mock_httpx_weather de conftest.py.
# Nuevo en Clase 4:
#   - test_get_weather_returns_correct_types: verifica tipos, no solo claves
#   - test_get_weather_raises_on_malformed_response: cubre el case _ del match
#   - test_get_weather_accepts_any_city: parametrize con 3 ciudades
# [CLASE 5 ->] Se añadiran tests async cuando migremos a httpx.AsyncClient.

"""Tests unitarios para pycommute.weather."""

from unittest.mock import MagicMock

import httpx
import pytest

from pycommute.weather import get_current_weather


def test_get_weather_returns_expected_fields(mock_httpx_weather: MagicMock) -> None:
    """Verifica que get_current_weather devuelve las keys correctas."""
    result = get_current_weather("Valencia", "fake-key")

    assert "city" in result
    assert "temperature" in result
    assert "description" in result


# [CLASE 4] Nuevo: separar verificacion de tipos en su propio test.
# Un test verifica UNA cosa — si este falla sabemos exactamente que es un problema
# de tipos, no de claves faltantes.
def test_get_weather_returns_correct_types(mock_httpx_weather: MagicMock) -> None:
    """Verifica que temperature es float, description y city son str."""
    result = get_current_weather("Valencia", "fake-key")

    assert isinstance(result["temperature"], float)
    assert isinstance(result["description"], str)
    assert isinstance(result["city"], str)


def test_get_weather_raises_on_bad_key(mocker) -> None:
    """Verifica que HTTPStatusError se propaga con una API key invalida (401).

    Con @retry configurado para ConnectError/TimeoutException unicamente,
    un HTTPStatusError no se reintenta — falla en el primer intento.
    """
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=MagicMock(),
        response=MagicMock(status_code=401),
    )
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response
    mocker.patch("pycommute.weather.httpx.Client", return_value=mock_client)

    with pytest.raises(httpx.HTTPStatusError):
        get_current_weather("Valencia", "key-invalida")


# [CLASE 4] Nuevo: testear el case _ del match en weather.py.
# Este test cubre el camino de error "Respuesta inesperada" que no estaba
# cubierto en Clase 3. Completa la cobertura del patron match/case.
def test_get_weather_raises_on_malformed_response(mocker) -> None:
    """Verifica que una respuesta sin las claves esperadas lanza ValueError."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"status": "ok"}  # sin 'main' ni 'weather'
    mock_response.raise_for_status.return_value = None
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response
    mocker.patch("pycommute.weather.httpx.Client", return_value=mock_client)

    with pytest.raises(ValueError, match="Respuesta inesperada"):
        get_current_weather("Valencia", "fake-key")


# [CLASE 4] Nuevo: parametrize — un test que corre 3 veces con distintas ciudades.
# El campo city del resultado viene del argumento de entrada, no del JSON de la API.
# Este test verifica ese contrato: lo que entra, sale.
@pytest.mark.parametrize("city", ["Valencia", "Madrid", "Barcelona"])
def test_get_weather_accepts_any_city(
    mock_httpx_weather: MagicMock, city: str
) -> None:
    """Verifica que el campo city del resultado refleja el argumento de entrada."""
    result = get_current_weather(city, "fake-key")

    assert result["city"] == city
