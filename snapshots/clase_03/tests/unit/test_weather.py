# [CLASE 3] Tests sin cambios respecto a Clase 2 — la firma de get_current_weather
# no cambió. El @retry con retry_if_exception_type(ConnectError, TimeoutException)
# no se activa con HTTPStatusError, así que los tests existentes siguen en verde.
# [CLASE 4 →] Se añadirán tests específicos para el retry:
# mock de ConnectError que verifica que la función reintenta exactamente 3 veces,
# y test de Settings con monkeypatch de variables de entorno.

"""Tests unitarios para pycommute.weather — Clase 3."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from pycommute.weather import get_current_weather


def test_get_weather_returns_expected_fields(weather_valencia_json: dict) -> None:
    """Verifica que get_current_weather devuelve las keys correctas."""
    mock_response = MagicMock()
    mock_response.json.return_value = weather_valencia_json
    mock_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response

    with patch("pycommute.weather.httpx.Client", return_value=mock_client):
        result = get_current_weather("Valencia", "fake_key")

    assert "city" in result
    assert "temperature" in result
    assert "description" in result
    assert result["city"] == "Valencia"
    assert isinstance(result["temperature"], float)
    assert isinstance(result["description"], str)


def test_get_weather_raises_on_bad_key() -> None:
    """Verifica que HTTPStatusError se propaga con una API key inválida (401).

    Con @retry configurado para ConnectError/TimeoutException únicamente,
    un HTTPStatusError no se reintenta — falla en el primer intento.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=MagicMock(),
        response=MagicMock(status_code=401),
    )

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response

    with patch("pycommute.weather.httpx.Client", return_value=mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            get_current_weather("Valencia", "key_invalida")
