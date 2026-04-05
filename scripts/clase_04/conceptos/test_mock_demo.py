import httpx

# La función real en nuestro código de producción


def get_traffic_status(city: str) -> str:
    response = httpx.get(f"https://api.traffic.com/v1/{city}")
    return response.json()["status"]

# El Test


def test_traffic_status_is_extracted_correctly(mocker):
    # 1. Secuestramos la función real
    mock_get = mocker.patch("httpx.get")

    # 2. Definimos la respuesta falsa (Encadenamiento de métodos)
    mock_get.return_value.json.return_value = {"status": "Heavy"}

    # 3. Ejecutamos nuestra lógica
    resultado = get_traffic_status("Madrid")

    # 4. Validamos estado y comportamiento
    assert resultado == "Heavy"
    mock_get.assert_called_once_with("https://api.traffic.com/v1/Madrid")
