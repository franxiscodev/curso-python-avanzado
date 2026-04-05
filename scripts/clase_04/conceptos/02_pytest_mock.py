"""Mocks con pytest-mock: aislar dependencias externas de red.

Demuestra mocker.patch para reemplazar httpx.get por un doble controlado:
- Happy path: la API responde OK -> se retorna el status directamente
- Sad path 1: timeout de red -> fallback gracil "UNKNOWN_TIMEOUT"
- Sad path 2: HTTP 500 -> se traduce a TrafficAPIError (excepcion de dominio)

mocker.patch("httpx.get") reemplaza el objeto en el namespace del modulo bajo test.
side_effect fuerza que el mock lance una excepcion en lugar de retornar un valor.
assert_called_once_with() verifica URL y timeout — no solo que se llamo.

Ejecutar (desde curso/):
    uv run pytest scripts/clase_04/conceptos/02_pytest_mock.py -v
"""

import httpx
import pytest

# --- 1. EXCEPCIÓN DE NUESTRO DOMINIO ---


class TrafficAPIError(Exception):
    """Excepción personalizada para aislar a nuestra app de los errores de httpx."""
    pass

# --- 2. NUESTRA LÓGICA DE NEGOCIO (El Adaptador) ---


def get_traffic_status(city: str) -> str:
    try:
        # Siempre configuramos timeout en el mundo real
        response = httpx.get(f"https://api.traffic.com/v1/{city}", timeout=2.0)

        # Si el status code es 4xx o 5xx, lanza httpx.HTTPStatusError
        response.raise_for_status()

        return response.json()["status"]

    except httpx.TimeoutException:
        # SAD PATH 1: Fallback grácil. Si hay timeout, asumimos tráfico desconocido
        return "UNKNOWN_TIMEOUT"

    except httpx.HTTPStatusError as e:
        # SAD PATH 2: Explosión controlada. Traducimos el error de librería a nuestro dominio
        raise TrafficAPIError(
            f"Fallo en la API de tráfico: HTTP {e.response.status_code}")

# --- 3. NUESTROS TESTS ---


def test_traffic_status_happy_path(mocker):
    """Prueba que el adaptador funciona cuando la red va bien."""
    mock_get = mocker.patch("httpx.get")
    mock_get.return_value.json.return_value = {"status": "Clear"}
    # raise_for_status no debe hacer nada en el happy path
    mock_get.return_value.raise_for_status.return_value = None

    assert get_traffic_status("Madrid") == "Clear"


def test_traffic_status_handles_timeout(mocker):
    """Prueba el SAD PATH 1: La red se queda colgada."""
    mock_get = mocker.patch("httpx.get")

    # side_effect = una excepcion: el mock lanza en lugar de retornar
    mock_get.side_effect = httpx.TimeoutException("Read timeout on socket")

    resultado = get_traffic_status("Barcelona")

    assert resultado == "UNKNOWN_TIMEOUT"
    # Verificamos URL y timeout — si el timeout cambia en produccion, este test lo detecta
    mock_get.assert_called_once_with(
        "https://api.traffic.com/v1/Barcelona", timeout=2.0)


def test_traffic_status_explodes_on_500_error(mocker):
    """Prueba el SAD PATH 2: La API devuelve un 500 Internal Server Error."""
    mock_get = mocker.patch("httpx.get")

    mock_response = mocker.MagicMock()
    mock_response.status_code = 500

    # HTTPStatusError requiere request y response — MagicMock basta para ambos
    mock_get.side_effect = httpx.HTTPStatusError(
        "Server Error", request=mocker.MagicMock(), response=mock_response
    )

    # El test verifica que lanza NUESTRA excepcion de dominio, no la de httpx
    with pytest.raises(TrafficAPIError, match="Fallo en la API de tráfico: HTTP 500"):
        get_traffic_status("Valencia")
