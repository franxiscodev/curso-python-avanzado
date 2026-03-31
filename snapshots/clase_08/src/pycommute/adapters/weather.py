"""Adaptador de OpenWeather — implementa WeatherPort.

# [CLASE 8] weather.py se mueve de src/pycommute/ a adapters/ y se convierte
# en clase. Antes (Clase 7): funciones sueltas get_current_weather().
# La logica match/case es identica — solo cambia el empaquetado.
# [CLASE 9 ->] El dict de retorno se reemplazara por WeatherResponse (Pydantic).
"""

from typing import Any

import httpx
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from pycommute.core.ports import WeatherPort  # noqa: F401 — cumple el protocolo

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


class OpenWeatherAdapter:
    """Adaptador concreto para la API de OpenWeatherMap.

    Implementa WeatherPort sin heredar de él — duck typing estructural.
    Si mañana cambia la API, solo cambia este archivo.
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
        reraise=True,
    )
    async def get_current_weather(
        self, city: str, api_key: str
    ) -> dict[str, Any]:
        """Obtiene el clima actual para una ciudad de forma asíncrona.

        Reintenta automáticamente hasta 3 veces ante fallos de red.

        Args:
            city: Nombre de la ciudad (ej. "Valencia").
            api_key: API key de OpenWeatherMap.

        Returns:
            Diccionario con temperature, description, city.

        Raises:
            httpx.HTTPStatusError: Si la API devuelve un error HTTP.
            ValueError: Si la respuesta tiene estructura inesperada.
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
                    "Clima obtenido: {temp:.0f}C, {desc}",
                    temp=temp,
                    desc=desc,
                )
                return {"temperature": temp, "description": desc, "city": city}
            case {"cod": code, "message": msg}:
                raise ValueError(f"API error {code}: {msg}")
            case _:
                raise ValueError(f"Respuesta inesperada de OpenWeather: {data}")
