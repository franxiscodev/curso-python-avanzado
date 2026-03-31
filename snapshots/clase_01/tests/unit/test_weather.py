# [CLASE 1] Tests mínimos: verifican que el contrato básico se cumple —
# las tres keys del dict resultado y la propagación de HTTPStatusError.
# Introducción rápida a pytest y mocks sin profundizar en técnica.
# [CLASE 4 →] En la clase de testing estos tests se expanden con:
# fixtures reutilizables, parametrización y cobertura de casos edge.

"""Tests unitarios para pycommute.weather — Clase 1.

Nota pedagógica: los mocks se explican brevemente en clase.
La Clase 4 profundiza en pytest, fixtures y mocking avanzado.
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from pycommute.weather import get_current_weather


def test_get_weather_returns_expected_fields(weather_valencia_json: dict) -> None:
    """Verifica que get_current_weather devuelve las keys correctas.

    Usa un mock de httpx.Client para evitar llamadas reales a la API.
    """
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
    """Verifica que HTTPStatusError se propaga con una API key inválida (401)."""
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
