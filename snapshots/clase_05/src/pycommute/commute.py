# [CLASE 5] commute.py: nuevo modulo orquestador — el corazon de Clase 5.
# Patron clave: dict compartido + funciones internas async para recoger resultados
# del task group. Weather y todas las rutas se lanzan en paralelo.
# Por que modulo separado: responsabilidad diferente (orquestar, no consultar).
# Weather y route no se conocen entre si — commute depende de ambos.
# [CLASE 8 ->] get_commute_info recibira los adaptadores por inyeccion de
# dependencias cuando migremos a arquitectura hexagonal.
"""Orquestador de PyCommute — ejecuta weather y route en paralelo.

Este módulo coordina las dos fuentes de datos usando
anyio.create_task_group() para ejecutarlas de forma concurrente.
"""

from typing import Any

import anyio
from loguru import logger

from pycommute.route import get_route
from pycommute.weather import get_current_weather


async def get_commute_info(
    city: str,
    origin: tuple[float, float],
    destination: tuple[float, float],
    profiles: list[str],
    weather_key: str,
    route_key: str,
) -> dict[str, Any]:
    """Obtiene clima y rutas en paralelo usando un task group.

    Lanza get_current_weather y todas las llamadas a get_route
    simultáneamente. El bloque async with espera a que todas
    completen antes de retornar.

    Args:
        city: Ciudad para consultar el clima.
        origin: Coordenadas de origen (lat, lon).
        destination: Coordenadas de destino (lat, lon).
        profiles: Lista de perfiles de ruta a consultar.
        weather_key: API key de OpenWeather.
        route_key: API key de OpenRouteService.

    Returns:
        Diccionario con:
            - weather (dict): resultado de get_current_weather.
            - routes (list[dict]): lista de resultados de get_route,
              uno por cada perfil.
    """
    results: dict[str, Any] = {}

    async def fetch_weather() -> None:
        results["weather"] = await get_current_weather(city, weather_key)

    async def fetch_routes() -> None:
        routes = []
        for profile in profiles:
            route = await get_route(origin, destination, profile, route_key)
            routes.append(route)
        results["routes"] = routes

    logger.info("Iniciando consultas en paralelo...")
    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch_weather)
        tg.start_soon(fetch_routes)

    return results
