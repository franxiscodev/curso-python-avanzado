"""Demo de Clase 5 — Benchmark: llamadas secuenciales vs paralelas.

Nota: demo actualizado en Clase 8 — CommuteService (DI) reemplaza get_commute_info standalone.
OpenWeatherAdapter y OpenRouteAdapter reemplazan las funciones directas.
Ver snapshots/clase_05/ para la version original.
Nota: demo actualizado en Clase 10 — CommuteResult reemplaza dict[str, Any].
Ver snapshots/clase_05/ para la version original.

Mide y compara el tiempo de ejecución entre consultar weather + route
de forma secuencial versus en paralelo con anyio.create_task_group().

Ejecutar desde curso/:
    uv run scripts/clase_05/demo_proyecto.py
"""

import time

import anyio
from loguru import logger

from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.config import settings
from pycommute.services.commute import CommuteService

CITY = "Valencia"
DESTINATION_CITY = "Madrid"
ORIGIN = (39.4697, -0.3763)
DESTINATION = (40.4168, -3.7038)
PROFILES = ["cycling-regular", "driving-car"]


async def run_sequential() -> tuple[dict, list]:
    """Ejecuta weather y routes de forma secuencial (una tras otra)."""
    weather_adapter = OpenWeatherAdapter()
    route_adapter = OpenRouteAdapter()

    weather = await weather_adapter.get_current_weather(CITY, settings.openweather_api_key)
    routes = []
    for profile in PROFILES:
        route = await route_adapter.get_route(ORIGIN, DESTINATION, profile, settings.openrouteservice_api_key)
        routes.append(route)
    return weather, routes


async def main() -> None:
    """Ejecuta el benchmark y muestra los resultados."""
    logger.info("=== Benchmark: secuencial vs paralelo ===")

    # Version secuencial
    logger.info("Ejecutando version secuencial...")
    t0 = time.perf_counter()
    weather_seq, routes_seq = await run_sequential()
    t_sequential = time.perf_counter() - t0
    logger.info("Tiempo secuencial: {t:.2f}s", t=t_sequential)

    # Version paralela con CommuteService
    logger.info("Ejecutando version paralela (anyio.create_task_group via CommuteService)...")
    service = CommuteService(
        weather=OpenWeatherAdapter(),
        route=OpenRouteAdapter(),
        cache=MemoryCacheAdapter(),
    )
    t0 = time.perf_counter()
    result = await service.get_commute_info(
        city=CITY,
        destination_city=DESTINATION_CITY,
        profiles=PROFILES,
        weather_key=settings.openweather_api_key,
        route_key=settings.openrouteservice_api_key,
    )
    t_parallel = time.perf_counter() - t0
    logger.info("Tiempo paralelo: {t:.2f}s", t=t_parallel)

    # Comparativa
    if t_parallel > 0:
        speedup = t_sequential / t_parallel
        logger.info("Mejora: {speedup:.2f}x mas rapido", speedup=speedup)

    # Resultados
    logger.info(
        "Clima: {temp:.0f}C, {desc}",
        temp=result.origin_weather.temperature,
        desc=result.origin_weather.description,
    )
    for route in result.routes:
        logger.info(
            "Ruta {profile}: {km} km, {min} min",
            profile=route.profile,
            km=route.distance_km,
            min=route.duration_min,
        )


anyio.run(main)
