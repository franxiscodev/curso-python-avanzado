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
    # Evitamos que raise_for_status haga algo
    mock_get.return_value.raise_for_status.return_value = None

    assert get_traffic_status("Madrid") == "Clear"


def test_traffic_status_handles_timeout(mocker):
    """Prueba el SAD PATH 1: La red se queda colgada."""
    mock_get = mocker.patch("httpx.get")

    # ¡LA MAGIA! En lugar de devolver algo, forzamos a que lance la excepción
    mock_get.side_effect = httpx.TimeoutException("Read timeout on socket")

    # La lógica debe atrapar esto y devolver el fallback
    resultado = get_traffic_status("Barcelona")

    assert resultado == "UNKNOWN_TIMEOUT"
    mock_get.assert_called_once_with(
        "https://api.traffic.com/v1/Barcelona", timeout=2.0)


def test_traffic_status_explodes_on_500_error(mocker):
    """Prueba el SAD PATH 2: La API devuelve un 500 Internal Server Error."""
    mock_get = mocker.patch("httpx.get")

    # Simulamos una respuesta fallida
    mock_response = mocker.MagicMock()
    mock_response.status_code = 500

    # Inyectamos la excepción de HTTPStatusError pasando la respuesta simulada
    mock_get.side_effect = httpx.HTTPStatusError(
        "Server Error", request=mocker.MagicMock(), response=mock_response
    )

    # Verificamos que nuestro código lanza NUESTRA excepción de dominio
    with pytest.raises(TrafficAPIError, match="Fallo en la API de tráfico: HTTP 500"):
        get_traffic_status("Valencia")
