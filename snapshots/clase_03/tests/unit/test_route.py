"""Tests unitarios para pycommute.route — Clase 2."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from pycommute.route import get_route

VALENCIA = (39.4697, -0.3763)
DESTINATION = (39.4870, -0.3560)


def test_get_route_returns_expected_fields(route_valencia_json: dict) -> None:
    """Verifica que get_route devuelve las keys y tipos correctos."""
    mock_response = MagicMock()
    mock_response.json.return_value = route_valencia_json
    mock_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response

    with patch("pycommute.route.httpx.Client", return_value=mock_client):
        result = get_route(VALENCIA, DESTINATION, "cycling-regular", "fake_key")

    assert "distance_km" in result
    assert "duration_min" in result
    assert "profile" in result
    assert result["profile"] == "cycling-regular"
    assert isinstance(result["distance_km"], float)
    assert isinstance(result["duration_min"], int)


def test_get_route_raises_on_bad_key() -> None:
    """Verifica que HTTPStatusError se propaga con una API key inválida (403)."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "403 Forbidden",
        request=MagicMock(),
        response=MagicMock(status_code=403),
    )

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response

    with patch("pycommute.route.httpx.Client", return_value=mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            get_route(VALENCIA, DESTINATION, "cycling-regular", "key_invalida")
