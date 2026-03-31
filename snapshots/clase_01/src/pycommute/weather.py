"""Módulo de consulta de clima — versión Clase 1 (simple, sin async ni retry).

Nota pedagógica: este módulo es intencionalmente simple.
Las Clases 2 y 3 lo mejorarán con Pattern Matching, Loguru y @retry.
"""

import httpx

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# [CLASE 1] Primera versión del cliente de clima.
# Intencionalmente simple: sin async, sin retry, sin logging estructurado.
# El foco es que funcione y que el alumno entienda httpx y .env.
def get_current_weather(city: str, api_key: str) -> dict:
    """Obtiene el clima actual para una ciudad usando la API de OpenWeather.

    Args:
        city: Nombre de la ciudad (ej. "Valencia").
        api_key: API key de OpenWeatherMap.

    Returns:
        Diccionario con las claves:
            - city (str): nombre de la ciudad devuelto por la API.
            - temperature (float): temperatura en grados Celsius.
            - description (str): descripción textual del clima.

    Raises:
        httpx.HTTPStatusError: Si la API devuelve un código de error
            (401 por key inválida, 404 por ciudad no encontrada, etc.).
    """
    params = {"q": city, "appid": api_key, "units": "metric"}

    with httpx.Client() as client:
        response = client.get(BASE_URL, params=params)
        # [CLASE 3 →] raise_for_status() es el punto donde @retry de tenacity
        # interceptará los fallos transitorios de red y reintentará automáticamente.
        # Loguru registrará cada intento con contexto estructurado en lugar de
        # propagar la excepción directamente al llamador.
        response.raise_for_status()
        data = response.json()

    # [CLASE 2 →] Este bloque de extracción directa será reemplazado por match/case.
    # Antes (Clase 1): acceso directo al dict — falla con KeyError si la API
    # cambia el formato o si falta algún campo.
    # Con match/case (Clase 2): cada estructura del JSON se maneja explícitamente,
    # con un caso de error legible en lugar de un traceback críptico.
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
    }
