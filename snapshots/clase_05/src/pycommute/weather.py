# [CLASE 5] weather.py migrado a async: async def + httpx.AsyncClient + await.
# Antes (Clase 4): def get_current_weather() con httpx.Client() sincrono.
# El contrato publico no cambia — mismos args, mismo retorno.
# El @retry de tenacity funciona igual con funciones async desde v8.x.
# [CLASE 6 ->] Se analizara el rendimiento con profiling para identificar
# si hay cuellos de botella en el parsing o la red.
"""Módulo de consulta de clima usando la API de OpenWeatherMap."""

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
async def get_current_weather(city: str, api_key: str) -> dict[str, Any]:
    """Obtiene el clima actual para una ciudad de forma asíncrona.

    Reintenta automáticamente hasta 3 veces ante fallos de red,
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

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
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
