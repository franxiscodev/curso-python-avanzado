"""Módulo de consulta de clima usando la API de OpenWeatherMap.

Nota pedagógica: versión Clase 2 — acceso directo al dict reemplazado por match/case.
Las Clases 3 y siguientes añaden logging estructurado y @retry.
"""

# [CLASE 2] match/case reemplaza el acceso directo a dict de la Clase 1.
# Antes (Clase 1): data["main"]["temp"] fallaba con KeyError si la API cambiaba formato.
# Ahora: el patrón describe exactamente la estructura esperada — si no encaja, falla
# con un ValueError descriptivo en lugar de un KeyError críptico.

import httpx

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_current_weather(city: str, api_key: str) -> dict:
    """Obtiene el clima actual para una ciudad usando la API de OpenWeather.

    Args:
        city: Nombre de la ciudad (ej. "Valencia").
        api_key: API key de OpenWeatherMap.

    Returns:
        Diccionario con las claves:
            - city (str): nombre de la ciudad (del argumento de entrada).
            - temperature (float): temperatura en grados Celsius.
            - description (str): descripción textual del clima.

    Raises:
        httpx.HTTPStatusError: Si la API devuelve un error HTTP.
        ValueError: Si la respuesta tiene una estructura inesperada.
    """
    params = {"q": city, "appid": api_key, "units": "metric"}

    with httpx.Client() as client:
        response = client.get(BASE_URL, params=params)
        # [CLASE 3 →] Este raise_for_status() será el punto de intercepción
        # de tenacity (@retry) y loguru registrará cada intento con contexto.
        response.raise_for_status()
        data = response.json()

    # [CLASE 2] match/case sobre la respuesta de OpenWeather.
    # El patrón extrae temp y desc en un solo paso — si la estructura no encaja,
    # el caso _ lanza ValueError en lugar de KeyError.
    match data:
        case {"main": {"temp": temp}, "weather": [{"description": desc}, *_]}:
            return {"temperature": temp, "description": desc, "city": city}
        case {"cod": code, "message": msg}:
            raise ValueError(f"API error {code}: {msg}")
        case _:
            raise ValueError(f"Respuesta inesperada de OpenWeather: {data}")
    # [CLASE 9 →] El dict de retorno será reemplazado por un modelo Pydantic V2
    # WeatherResult que valida los tipos en el momento de creación.
