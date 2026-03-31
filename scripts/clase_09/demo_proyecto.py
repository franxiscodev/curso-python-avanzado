"""Demo Clase 9 — Contratos de datos con Pydantic V2 en PyCommute.

Demuestra:
- WeatherData y RouteData validados en la frontera del sistema
- CommuteResult con best_route calculado automaticamente
- ValidationError cuando un adaptador devuelve datos invalidos
- model_dump() para serializar el resultado completo

Ejecutar desde curso/:
    # Windows (PowerShell)
    uv run scripts/clase_09/demo_proyecto.py

    # Linux
    uv run scripts/clase_09/demo_proyecto.py
"""

import anyio
from loguru import logger
from pydantic import ValidationError

from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.config import settings
from pycommute.core.models import RouteData, WeatherData
from pycommute.services.commute import CommuteService


async def main() -> None:
    """Ejecuta el demo completo de Clase 9."""

    # ── Demo: ValidationError en la frontera ─────────────────────────
    logger.info("=== Demo: ValidationError en la frontera ===")

    logger.info("Intentando crear WeatherData con temperatura de 999C...")
    try:
        WeatherData(temperature=999.0, description="hot", city="Venus")
    except ValidationError as e:
        for error in e.errors():
            logger.warning(
                "ValidationError: {loc} — {msg}",
                loc=error["loc"][0],
                msg=error["msg"],
            )

    logger.info("Intentando crear RouteData con perfil invalido...")
    try:
        RouteData(distance_km=2.0, duration_min=8.0, profile="flying-car")
    except ValidationError as e:
        for error in e.errors():
            logger.warning(
                "ValidationError: {loc} — {msg}",
                loc=error["loc"][0],
                msg=error["msg"],
            )

    # ── Demo: datos validos y normalizacion ──────────────────────────
    logger.info("=== Demo: normalizacion automatica ===")
    w = WeatherData(temperature=13.587, description="  Partly Cloudy  ", city="Valencia")
    logger.info(
        "WeatherData creado: temp={temp} (redondeado), desc='{desc}' (normalizado)",
        temp=w.temperature,
        desc=w.description,
    )

    # ── Consulta real con adaptadores ────────────────────────────────
    logger.info("=== Consulta real: Valencia -> Madrid ===")
    service = CommuteService(
        weather=OpenWeatherAdapter(),
        route=OpenRouteAdapter(),
        cache=MemoryCacheAdapter(),
    )

    result = await service.get_commute_info(
        city="Valencia",
        destination_city="Madrid",
        profiles=["cycling-regular", "driving-car", "foot-walking"],
        weather_key=settings.openweather_api_key,
        route_key=settings.openrouteservice_api_key,
    )

    # Nota: demo actualizado en Clase 10 — CommuteResult ahora tiene
    # origin_weather y destination_weather en lugar de weather.
    # Ver snapshots/clase_09/ para la version original.
    logger.info(
        "Clima validado: WeatherData(temperature={temp}, description='{desc}', city='{city}')",
        temp=result.origin_weather.temperature,
        desc=result.origin_weather.description,
        city=result.origin_weather.city,
    )

    logger.info("Rutas validadas ({n} RouteData):", n=len(result.routes))
    for route in result.routes:
        logger.info(
            "  RouteData(distance_km={km}, duration_min={min}, profile='{p}')",
            km=route.distance_km,
            min=route.duration_min,
            p=route.profile,
        )

    # best_route calculado automaticamente en CommuteResult
    best = result.best_route
    logger.info(
        "Mejor ruta (model_validator): {profile} — {dur} min",
        profile=best.profile,
        dur=best.duration_min,
    )

    # Serializacion completa
    logger.info("=== Serializacion con model_dump() ===")
    data = result.model_dump()
    logger.info("Claves en CommuteResult: {keys}", keys=list(data.keys()))
    logger.info("Historial: {n} consultas registradas", n=len(service.history))


anyio.run(main)
