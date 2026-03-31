"""Módulo de consulta de rutas usando la API de OpenRouteService.

Nota pedagógica: versión Clase 2 — mismo patrón match/case que weather.py,
aplicado al JSON más complejo (GeoJSON) de OpenRouteService.
"""

# [CLASE 2] Nuevo módulo introducido en esta clase.
# Patrón "un módulo por fuente de datos" — weather.py sabe de clima,
# route.py sabe de rutas. Los mezclamos evita que un cambio en ORS rompa clima.
# [CLASE 8 →] Cada módulo se convertirá en un adaptador de la arquitectura
# hexagonal — la separación ya estará hecha cuando lleguemos ahí.

from typing import Any

import httpx

BASE_URL = "https://api.openrouteservice.org/v2/directions"


def get_route(
    origin: tuple[float, float],
    destination: tuple[float, float],
    profile: str,
    api_key: str,
) -> dict[str, Any]:
    """Obtiene una ruta entre dos puntos usando la API de OpenRouteService.

    Args:
        origin: Coordenadas de origen como (lat, lon).
        destination: Coordenadas de destino como (lat, lon).
        profile: Perfil de transporte. Valores válidos:
            ``"cycling-regular"``, ``"driving-car"``, ``"foot-walking"``.
        api_key: API key de OpenRouteService.

    Returns:
        Diccionario con las claves:
            - distance_km (float): distancia en kilómetros (1 decimal).
            - duration_min (int): duración estimada en minutos.
            - profile (str): perfil de transporte usado.

    Raises:
        httpx.HTTPStatusError: Si la API devuelve un error HTTP.
        ValueError: Si la respuesta tiene una estructura inesperada.
    """
    # ORS usa [lon, lat] — invertimos la convención (lat, lon) de entrada
    start = f"{origin[1]},{origin[0]}"
    end = f"{destination[1]},{destination[0]}"

    headers = {
        "Authorization": api_key,
        "Accept": "application/json, application/geo+json",
    }
    params = {"start": start, "end": end}

    with httpx.Client() as client:
        response = client.get(
            f"{BASE_URL}/{profile}",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

    # [CLASE 2] El GeoJSON de ORS tiene más niveles de anidación que OpenWeather.
    # match/case descompone la estructura en un solo patrón legible:
    # features → primer feature → properties → summary → distance y duration.
    # El `*_` captura posibles features adicionales sin romper el patrón.
    match data:
        case {"features": [{"properties": {"summary": {"distance": dist, "duration": dur}}}, *_]}:
            return {
                "distance_km": round(dist / 1000, 1),
                "duration_min": round(dur / 60),
                "profile": profile,
            }
        case {"error": {"code": code, "message": msg}}:
            raise ValueError(f"ORS error {code}: {msg}")
        case _:
            raise ValueError(f"Respuesta inesperada de OpenRouteService: {data}")
    # [CLASE 9 →] El dict de retorno será un modelo Pydantic V2 RouteResult.
