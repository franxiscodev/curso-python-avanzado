# [CLASE 7] Sin cambios en este archivo — commute.py se mantiene igual que Clase 6.
# El foco de Clase 7 es ranking.py (heapq) e history.py (deque + dataclass).
# [CLASE 8 ->] commute.py se convierte en caso de uso hexagonal:
#              recibe puertos (WeatherPort, RoutePort) en lugar de importarlos.

"""Orquestador de PyCommute — ejecuta weather y route en paralelo.

Este módulo coordina las dos fuentes de datos usando
anyio.create_task_group() para ejecutarlas de forma concurrente.
Incluye soporte para iteración lazy de rutas y profiling con cProfile.
"""

import cProfile
import io
import pstats
from typing import Any, AsyncGenerator

import anyio
from loguru import logger

from pycommute.cache import get_coordinates
from pycommute.route import get_route
from pycommute.weather import get_current_weather


async def iter_routes(
    origin: tuple[float, float],
    destination: tuple[float, float],
    profiles: list[str],
    api_key: str,
) -> AsyncGenerator[dict[str, Any], None]:
    """Genera rutas de forma lazy — una por una sin cargar todas en memoria.

    Útil cuando se consultan muchos perfiles y se procesa cada resultado
    a medida que llega, sin esperar al resto.

    Args:
        origin: Coordenadas de origen (lat, lon).
        destination: Coordenadas de destino (lat, lon).
        profiles: Lista de perfiles de ruta a consultar.
        api_key: API key de OpenRouteService.

    Yields:
        Diccionario con distance_km, duration_min y profile para cada perfil.
    """
    for profile in profiles:
        route = await get_route(origin, destination, profile, api_key)
        yield route


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


async def get_commute_info_profiled(
    city: str,
    origin: tuple[float, float],
    destination: tuple[float, float],
    profiles: list[str],
    weather_key: str,
    route_key: str,
) -> dict[str, Any]:
    """Versión perfilada de get_commute_info para diagnóstico de rendimiento.

    Ejecuta get_commute_info bajo cProfile y registra las 10 funciones
    más lentas por tiempo acumulado en el log de debug.

    Args:
        city: Ciudad para consultar el clima.
        origin: Coordenadas de origen (lat, lon).
        destination: Coordenadas de destino (lat, lon).
        profiles: Lista de perfiles de ruta a consultar.
        weather_key: API key de OpenWeather.
        route_key: API key de OpenRouteService.

    Returns:
        Mismo resultado que get_commute_info.
    """
    profiler = cProfile.Profile()
    profiler.enable()
    result = await get_commute_info(
        city=city,
        origin=origin,
        destination=destination,
        profiles=profiles,
        weather_key=weather_key,
        route_key=route_key,
    )
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(10)
    logger.debug("cProfile:\n{stats}", stats=stream.getvalue())

    return result


def get_origin_destination(
    origin_city: str,
    destination_city: str,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Resuelve coordenadas de origen y destino desde nombres de ciudad.

    Usa el cache de coordenadas para evitar búsquedas repetidas.

    Args:
        origin_city: Ciudad de origen.
        destination_city: Ciudad de destino.

    Returns:
        Tupla de (origin_coords, destination_coords).

    Raises:
        ValueError: Si alguna ciudad no está en el registro.
    """
    origin = get_coordinates(origin_city)
    destination = get_coordinates(destination_city)
    return origin, destination
