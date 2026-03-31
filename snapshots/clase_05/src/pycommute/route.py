# [CLASE 5] route.py migrado a async: mismo patron que weather.py.
# Antes (Clase 4): def get_route() con httpx.Client() sincrono.
# Sin @retry — ORS no tiene errores de red transitorios frecuentes.
# [CLASE 6 ->] Sin cambios previstos en este modulo.
"""Módulo de consulta de rutas usando la API de OpenRouteService."""

from typing import Any

import httpx

BASE_URL = "https://api.openrouteservice.org/v2/directions"


async def get_route(
    origin: tuple[float, float],
    destination: tuple[float, float],
    profile: str,
    api_key: str,
) -> dict[str, Any]:
    """Obtiene una ruta entre dos puntos de forma asíncrona.

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
        httpx.HTTPStatusError: Si la API devuelve un error HTTP
            (403 por cuota agotada, 404 por ruta no encontrada, etc.).
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

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/{profile}",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

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
