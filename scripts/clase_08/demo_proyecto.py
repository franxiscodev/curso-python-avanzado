"""Demo Clase 8 — Arquitectura Hexagonal con Puertos y Adaptadores.

Nota: demo actualizado en Clase 10 — CommuteResult reemplaza dict[str, Any].
Ver snapshots/clase_08/ para la version original.

Demuestra:
- CommuteService recibe sus dependencias por constructor (inyeccion de dependencias)
- Los Protocolos (WeatherPort, RoutePort, CachePort) definen los contratos
- Los adaptadores se pueden intercambiar sin modificar el servicio
- isinstance() con @runtime_checkable verifica conformidad estructural

Ejecutar desde curso/:
    # Windows (PowerShell)
    uv run scripts/clase_08/demo_proyecto.py

    # Linux
    uv run scripts/clase_08/demo_proyecto.py
"""

import anyio
from loguru import logger

from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.config import settings
from pycommute.core.ports import CachePort, RoutePort, WeatherPort
from pycommute.services.commute import CommuteService


async def main() -> None:
    """Ejecuta el demo de arquitectura hexagonal."""
    logger.info("=== Verificacion de Protocolos ===")

    weather_adapter = OpenWeatherAdapter()
    route_adapter = OpenRouteAdapter()
    cache_adapter = MemoryCacheAdapter()

    # isinstance funciona sin herencia — duck typing estructural
    logger.info("OpenWeatherAdapter satisface WeatherPort: {ok}", ok=isinstance(weather_adapter, WeatherPort))
    logger.info("OpenRouteAdapter satisface RoutePort:    {ok}", ok=isinstance(route_adapter, RoutePort))
    logger.info("MemoryCacheAdapter satisface CachePort:  {ok}", ok=isinstance(cache_adapter, CachePort))

    # Construccion del servicio con inyeccion de dependencias
    logger.info("=== Construccion del servicio ===")
    service = CommuteService(
        weather=weather_adapter,
        route=route_adapter,
        cache=cache_adapter,
    )
    logger.info("CommuteService creado con adaptadores reales")

    # Consulta completa
    logger.info("=== Consulta Valencia -> Madrid ===")
    result = await service.get_commute_info(
        city="Valencia",
        destination_city="Madrid",
        profiles=["cycling-regular", "driving-car", "foot-walking"],
        weather_key=settings.openweather_api_key,
        route_key=settings.openrouteservice_api_key,
    )

    logger.info(
        "Clima en Valencia: {temp:.0f}C, {desc}",
        temp=result.origin_weather.temperature,
        desc=result.origin_weather.description,
    )

    logger.info("=== Rutas (ordenadas por tiempo) ===")
    for route in result.routes:
        logger.info(
            "  {profile:<20} {dist} km, {dur} min",
            profile=route.profile + ":",
            dist=route.distance_km,
            dur=route.duration_min,
        )

    # Historial se almacena automaticamente en el servicio
    logger.info("Consultas en historial: {n}", n=len(service.history))
    for entry in service.history.get_recent():
        logger.info("  {entry}", entry=str(entry))


anyio.run(main)
