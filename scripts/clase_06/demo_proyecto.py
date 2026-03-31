"""Demo Clase 6 — Cache, generadores y profiling en PyCommute.

Nota: demo actualizado en Clase 8 — adaptadores reemplazan funciones standalone.
cache_info y get_coordinates vienen de adapters.cache; iter_routes se implementa
como generador local; CommuteService reemplaza get_commute_info_profiled.
Ver snapshots/clase_06/ para la version original.
Nota: demo actualizado en Clase 10 — CommuteResult reemplaza dict[str, Any].
Ver snapshots/clase_06/ para la version original.

Demuestra:
- Cache hits de lru_cache en get_coordinates
- Iteracion lazy de rutas con AsyncGenerator
- Profiling con cProfile
"""

import cProfile
import io
import pstats
from typing import AsyncGenerator

import anyio
from loguru import logger

from pycommute.adapters.cache import MemoryCacheAdapter, cache_info, get_coordinates
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.config import settings
from pycommute.services.commute import CommuteService


async def iter_routes(
    origin: tuple[float, float],
    destination: tuple[float, float],
    profiles: list[str],
    api_key: str,
) -> AsyncGenerator[object, None]:
    """AsyncGenerator: produce rutas una a una (lazy)."""
    adapter = OpenRouteAdapter()
    for profile in profiles:
        yield await adapter.get_route(origin, destination, profile, api_key)


async def main() -> None:
    """Ejecuta el demo completo de Clase 6."""

    # Cache de coordenadas
    logger.info("=== Cache de coordenadas ===")

    origin = get_coordinates("Valencia")
    logger.info("Coordenadas Valencia: {coords}", coords=origin)
    logger.info("Cache tras primera llamada: {info}", info=cache_info())

    get_coordinates("Valencia")
    logger.info("Cache tras segunda llamada: {info}", info=cache_info())

    destination = get_coordinates("Madrid")
    logger.info("Coordenadas Madrid: {coords}", coords=destination)
    logger.info("Cache tras consultar Madrid: {info}", info=cache_info())

    # Generador de rutas
    logger.info("=== Generador de rutas (lazy) ===")
    profiles = ["cycling-regular", "driving-car", "foot-walking"]
    logger.info("Procesando {n} rutas con generador...", n=len(profiles))

    i = 1
    async for route in iter_routes(origin, destination, profiles, settings.openrouteservice_api_key):
        logger.info(
            "Ruta {i}: {dist} km, {dur} min ({profile})",
            i=i,
            dist=route.distance_km,
            dur=route.duration_min,
            profile=route.profile,
        )
        i += 1

    # Profiling
    logger.info("=== Profiling con cProfile ===")
    service = CommuteService(
        weather=OpenWeatherAdapter(),
        route=OpenRouteAdapter(),
        cache=MemoryCacheAdapter(),
    )

    pr = cProfile.Profile()
    pr.enable()
    result = await service.get_commute_info(
        city="Valencia",
        destination_city="Madrid",
        profiles=["cycling-regular", "driving-car"],
        weather_key=settings.openweather_api_key,
        route_key=settings.openrouteservice_api_key,
    )
    pr.disable()

    buf = io.StringIO()
    ps = pstats.Stats(pr, stream=buf).sort_stats("cumulative")
    ps.print_stats(10)
    logger.info("Top 10 funciones por tiempo acumulado:\n{stats}", stats=buf.getvalue())

    logger.info(
        "Clima: {temp}C, {desc}",
        temp=result.origin_weather.temperature,
        desc=result.origin_weather.description,
    )
    logger.info("Cache final: {info}", info=cache_info())


anyio.run(main)
