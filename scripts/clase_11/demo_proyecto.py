"""Demo Clase 11 — IA Local y Fallback: Ollama + patron de resiliencia.

Demuestra:
- FallbackAIAdapter: Gemini primero, Ollama si falla
- Logs de conmutacion automatica
- Cambio de modelo sin tocar el servicio

Ejecutar desde la raiz del repo:
    # Windows (PowerShell)
    uv run python scripts/clase_11/demo_proyecto.py

    # Linux
    uv run python scripts/clase_11/demo_proyecto.py

Requisitos:
    - GOOGLE_API_KEY en .env — para Gemini (primario)
    - Ollama corriendo con gemma3:1b — para fallback local
      ollama serve && ollama pull gemma3:1b

Modo fallback forzado:
    Poner GOOGLE_API_KEY=invalid en .env para ver la conmutacion a Ollama.
"""

import anyio
from loguru import logger

from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.adapters.fallback_ai import FallbackAIAdapter
from pycommute.adapters.gemini import GeminiAdapter
from pycommute.adapters.ollama_adapter import OllamaAdapter
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.config import settings
from pycommute.services.commute import CommuteService

CITY = "Valencia"
DESTINATION_CITY = "Madrid"
PROFILES = ["cycling-regular", "driving-car", "foot-walking"]


async def main() -> None:
    """Ejecuta el demo completo de Clase 11."""

    # ── Configurar adaptadores de IA ─────────────────────────────────
    ollama_adapter = OllamaAdapter(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
    )

    if settings.google_api_key:
        gemini_adapter = GeminiAdapter(
            api_key=settings.google_api_key,
            model=settings.gemini_model,
        )
        ai_adapter = FallbackAIAdapter(
            primary=gemini_adapter,
            secondary=ollama_adapter,
        )
        google_key = settings.google_api_key
        logger.info(
            "FallbackAIAdapter configurado: GeminiAdapter -> OllamaAdapter ({model})",
            model=settings.ollama_model,
        )
    else:
        ai_adapter = ollama_adapter
        google_key = None
        logger.warning(
            "GOOGLE_API_KEY no configurada — usando OllamaAdapter directamente"
        )

    service = CommuteService(
        weather=OpenWeatherAdapter(),
        route=OpenRouteAdapter(),
        cache=MemoryCacheAdapter(),
        ai=ai_adapter,
    )

    # ── Consulta: 3 tareas en paralelo ───────────────────────────────
    logger.info(
        "Consultando {origin} -> {dest} con FallbackAI...",
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

    # ── Resultados de clima ──────────────────────────────────────────
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
        marker = " <- mejor" if route == result.best_route else ""
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
        logger.info("(Sin recomendacion IA — Ollama no disponible)")

    logger.info("Historial: {n} consultas registradas", n=len(service.history))


anyio.run(main)
