"""Demo Clase 7 — Ranking con heapq e historial con deque en PyCommute.

Nota: demo actualizado en Clase 8 — CommuteService (DI) reemplaza get_commute_info standalone.
Imports de ranking e history ahora vienen de core/. Ver snapshots/clase_07/ para la version original.
Nota: demo actualizado en Clase 10 — CommuteResult reemplaza dict[str, Any].
Ver snapshots/clase_07/ para la version original.

Demuestra:
- Ranking de rutas por tiempo y distancia con rank_routes_by_time()
- Mejor ruta en O(n) con get_best_route()
- Historial con maxlen — descarte automatico de consultas antiguas
"""

import anyio
from loguru import logger

from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.config import settings
from pycommute.core.history import ConsultaHistory
from pycommute.core.models import ConsultaEntry
from pycommute.core.ranking import get_best_route, rank_routes_by_time
from pycommute.services.commute import CommuteService

PROFILES = ["cycling-regular", "driving-car", "foot-walking"]
history = ConsultaHistory(maxlen=5)


def _make_service() -> CommuteService:
    return CommuteService(
        weather=OpenWeatherAdapter(),
        route=OpenRouteAdapter(),
        cache=MemoryCacheAdapter(),
    )


async def consultar(city_origin: str, city_dest: str) -> object:
    """Realiza una consulta completa y la registra en el historial."""
    service = _make_service()
    result = await service.get_commute_info(
        city=city_origin,
        destination_city=city_dest,
        profiles=PROFILES,
        weather_key=settings.openweather_api_key,
        route_key=settings.openrouteservice_api_key,
    )
    history.add(ConsultaEntry(city=city_origin, profiles=PROFILES, result=result))
    return result


async def main() -> None:
    """Ejecuta el demo completo de Clase 7."""
    # Consulta principal
    logger.info("=== Consulta Valencia -> Madrid ===")
    result = await consultar("Valencia", "Madrid")

    logger.info(
        "Clima en Valencia: {temp}C, {desc}",
        temp=result.origin_weather.temperature,
        desc=result.origin_weather.description,
    )

    # Ranking por tiempo
    logger.info("=== Rutas rankeadas por tiempo (mejor primero) ===")
    ranked = rank_routes_by_time(result.routes)
    for i, route in enumerate(ranked, 1):
        logger.info(
            "  {i}. {profile:<20} {dist} km, {dur} min",
            i=i,
            profile=route.profile + ":",
            dist=route.distance_km,
            dur=route.duration_min,
        )

    # Mejor ruta por distancia
    best = get_best_route(result.routes, by="distance")
    logger.info(
        "Ruta mas corta: {profile} ({dist} km)",
        profile=best.profile,
        dist=best.distance_km,
    )

    # Segunda consulta para demostrar historial con multiples entradas
    logger.info("=== Segunda consulta: Madrid -> Valencia ===")
    await consultar("Madrid", "Valencia")

    # Historial (maxlen=5)
    logger.info("=== Historial (ultimas {n} consultas) ===", n=len(history))
    for entry in history.get_recent():
        logger.info("  {entry}", entry=str(entry))


anyio.run(main)
