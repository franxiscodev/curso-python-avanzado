"""Demo de la Clase 3 — Loguru + Pydantic-Settings + @retry.

Nota: demo actualizado en Clase 5 — get_current_weather y get_route son ahora async.
Nota: demo actualizado en Clase 8 — OpenWeatherAdapter y OpenRouteAdapter reemplazan
      las funciones standalone. Ver snapshots/clase_03/ para la version original.
Nota: demo actualizado — get_current_weather() devuelve WeatherData (Pydantic) desde Clase 9.
Ver snapshots/clase_01/, clase_02/, clase_03/ para las versiones originales.

Settings se valida al importar config — si falta una key en .env,
la app lanza ValidationError antes de ejecutar nada.

Ejecutar:
    # Windows (PowerShell)
    uv run python scripts/clase_03/demo_proyecto.py

    # Linux
    uv run python scripts/clase_03/demo_proyecto.py
"""

import anyio
from loguru import logger

import pycommute
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.config import settings

CITY = "Valencia"
# Coordenadas (lat, lon): Valencia centro → barrio del Carmen
ORIGIN = (39.4697, -0.3763)
DESTINATION = (39.4756, -0.3884)

PROFILE_LABELS = {
    "cycling-regular": "bicicleta",
    "driving-car": "coche",
}


async def main() -> None:
    """Ejecuta la demo de clima y rutas con configuración validada."""
    logger.info("PyCommute v{version} iniciado", version=pycommute.__version__)

    weather_adapter = OpenWeatherAdapter()
    route_adapter = OpenRouteAdapter()

    weather = await weather_adapter.get_current_weather(CITY, settings.openweather_api_key)
    logger.info(
        "Clima en {city}: {temp:.0f}°C, {desc}",
        city=CITY,
        temp=weather.temperature,
        desc=weather.description,
    )

    for profile in ["cycling-regular", "driving-car"]:
        route = await route_adapter.get_route(ORIGIN, DESTINATION, profile, settings.openrouteservice_api_key)
        label = PROFILE_LABELS[profile]
        logger.info(
            "Ruta encontrada: {km} km, {min} min en {label}",
            km=route["distance_km"],
            min=route["duration_min"],
            label=label,
        )


anyio.run(main)
