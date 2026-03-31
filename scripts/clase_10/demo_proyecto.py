"""Demo Clase 10 — IA Cloud: Gemini API en PyCommute.

Demuestra:
- Consulta de clima de ORIGEN y DESTINO en paralelo
- GeminiAdapter generando recomendacion estructurada
- AIRecommendation con outfit_tips y departure_advice
- CommuteResult completo con best_route y ai_recommendation

Ejecutar desde curso/:
    # Windows (PowerShell)
    uv run scripts/clase_10/demo_proyecto.py

    # Linux
    uv run scripts/clase_10/demo_proyecto.py

Requiere GOOGLE_API_KEY en .env para la recomendacion IA.
Sin la key, el demo muestra el CommuteResult sin IA.
"""

import anyio
from loguru import logger

from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.adapters.gemini import GeminiAdapter
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.config import settings
from pycommute.services.commute import CommuteService

CITY = "Valencia"
DESTINATION_CITY = "Madrid"
PROFILES = ["cycling-regular", "driving-car", "foot-walking"]


async def main() -> None:
    """Ejecuta el demo completo de Clase 10."""

    # ── Configurar adaptadores ────────────────────────────────────────
    ai_adapter = None
    google_key = None

    if settings.google_api_key:
        ai_adapter = GeminiAdapter(api_key=settings.google_api_key, model=settings.gemini_model)
        google_key = settings.google_api_key
        logger.info("GeminiAdapter configurado — se generara recomendacion IA")
    else:
        logger.warning(
            "GOOGLE_API_KEY no configurada — demo sin recomendacion IA"
        )

    service = CommuteService(
        weather=OpenWeatherAdapter(),
        route=OpenRouteAdapter(),
        cache=MemoryCacheAdapter(),
        ai=ai_adapter,
    )

    # ── Consulta: 3 tareas en paralelo ───────────────────────────────
    logger.info(
        "Consultando clima {origin} -> {dest} en paralelo...",
        origin=CITY,
        dest=DESTINATION_CITY,
    )

    result = await service.get_commute_info(
        city=CITY,
        destination_city=DESTINATION_CITY,
        profiles=PROFILES,
        weather_key=settings.openweather_api_key,
        route_key=settings.openrouteservice_api_key,
        google_key=google_key,
    )

    # ── Resultados ───────────────────────────────────────────────────
    logger.info(
        "{city}: {temp}C, {desc}",
        city=result.origin_city,
        temp=result.origin_weather.temperature,
        desc=result.origin_weather.description,
    )
    logger.info(
        "{city}: {temp}C, {desc}",
        city=result.destination_city,
        temp=result.destination_weather.temperature,
        desc=result.destination_weather.description,
    )

    logger.info("Rutas disponibles ({n}):", n=len(result.routes))
    for route in result.routes:
        marker = " ← mejor" if route == result.best_route else ""
        logger.info(
            "  {profile}: {km}km, {min}min{marker}",
            profile=route.profile,
            km=route.distance_km,
            min=route.duration_min,
            marker=marker,
        )

    # ── Recomendacion IA ─────────────────────────────────────────────
    if result.ai_recommendation:
        rec = result.ai_recommendation
        logger.info("=== Recomendacion IA ===")
        logger.info(
            "Transporte sugerido: {profile} (confianza: {conf})",
            profile=rec.suggested_profile,
            conf=rec.confidence,
        )
        logger.info("Recomendacion: {rec}", rec=rec.recommendation)
        logger.info("Razonamiento: {r}", r=rec.reasoning)
        if rec.outfit_tips:
            logger.info("Vestimenta: {tips}", tips=", ".join(rec.outfit_tips))
        if rec.departure_advice:
            logger.info("Consejo de salida: {advice}", advice=rec.departure_advice)
    else:
        logger.info("(Sin recomendacion IA — configura GOOGLE_API_KEY en .env)")

    logger.info("Historial: {n} consultas registradas", n=len(service.history))


anyio.run(main)
