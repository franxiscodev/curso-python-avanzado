"""Módulo de consulta de clima usando la API de OpenWeatherMap.

Nota pedagógica: versión Clase 3 — loguru + @retry + Pydantic-Settings.
"""

# [CLASE 3] Tres cambios sobre la versión de Clase 2:
# 1. logger (loguru) reemplaza el silencio — toda actividad queda registrada.
# 2. @retry con condición: solo reintenta errores de red (ConnectError/Timeout),
#    no errores HTTP deterministas como 401 o 404.
# 3. La firma no cambia — api_key sigue siendo parámetro para facilitar el testing.
#    En el demo se pasa settings.openweather_api_key.

# [CLASE 4 →] Los tests se expandirán para probar el comportamiento del @retry
# con mocks de ConnectError, verificando que reintenta 3 veces y no más.
# [CLASE 8 →] logger.bind() se usará para añadir contexto de request_id
# en la arquitectura hexagonal.

from typing import Any

import httpx
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
def get_current_weather(city: str, api_key: str) -> dict[str, Any]:
    """Obtiene el clima actual para una ciudad usando la API de OpenWeather.

    Reintenta automáticamente hasta 3 veces ante fallos de red transitorios,
    con 1 segundo de espera entre intentos.

    Args:
        city: Nombre de la ciudad (ej. "Valencia").
        api_key: API key de OpenWeatherMap.

    Returns:
        Diccionario con las claves:
            - city (str): nombre de la ciudad (del argumento de entrada).
            - temperature (float): temperatura en grados Celsius.
            - description (str): descripción textual del clima.

    Raises:
        httpx.HTTPStatusError: Si la API devuelve un error HTTP no transitorio.
        ValueError: Si la respuesta tiene una estructura inesperada.
    """
    logger.info("Consultando clima para {city}", city=city)
    params = {"q": city, "appid": api_key, "units": "metric"}

    with httpx.Client() as client:
        response = client.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

    logger.debug("Respuesta recibida: {data}", data=data)

    match data:
        case {"main": {"temp": temp}, "weather": [{"description": desc}, *_]}:
            logger.info(
                "Clima obtenido: {temp:.0f}°C, {desc}",
                temp=temp,
                desc=desc,
            )
            return {"temperature": temp, "description": desc, "city": city}
        case {"cod": code, "message": msg}:
            raise ValueError(f"API error {code}: {msg}")
        case _:
            raise ValueError(f"Respuesta inesperada de OpenWeather: {data}")
