"""Adaptador de OpenRouteService — implementa RoutePort.

# [CLASE 8] route.py se mueve de src/pycommute/ a adapters/ y se convierte
# en clase. Antes (Clase 7): funcion suelta get_route().
# La logica match/case es identica — solo cambia el empaquetado.
# [CLASE 9 ->] El dict de retorno se reemplazara por RouteResponse (Pydantic).
"""

from typing import Any

import httpx
from loguru import logger

from pycommute.core.ports import RoutePort  # noqa: F401 — cumple el protocolo

BASE_URL = "https://api.openrouteservice.org/v2/directions"


class OpenRouteAdapter:
    """Adaptador concreto para la API de OpenRouteService.

    Implementa RoutePort sin heredar de él — duck typing estructural.
    Si mañana cambia la API, solo cambia este archivo.
    """

    async def get_route(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        profile: str,
        api_key: str,
    ) -> dict[str, Any]:
        """Obtiene una ruta entre dos puntos de forma asíncrona.

        Args:
            origin: Coordenadas de origen como (lat, lon).
            destination: Coordenadas de destino como (lat, lon).
            profile: Perfil de transporte (cycling-regular, driving-car, foot-walking).
            api_key: API key de OpenRouteService.

        Returns:
            Diccionario con distance_km, duration_min, profile.

        Raises:
            httpx.HTTPStatusError: Si la API devuelve un error HTTP.
            ValueError: Si la respuesta tiene estructura inesperada.
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

        logger.debug("Respuesta ORS: {profile}", profile=profile)

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
