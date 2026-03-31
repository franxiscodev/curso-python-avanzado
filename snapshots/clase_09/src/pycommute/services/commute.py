"""Servicio de movilidad — orquesta usando puertos inyectados.

# [CLASE 9] get_commute_info ahora devuelve CommuteResult en lugar de dict.
# Antes (Clase 8): return {"weather": ..., "routes": ...}
# Ahora: return CommuteResult(weather=weather_data, routes=route_list)
# Pydantic calcula best_route automaticamente en el model_validator.
# [CLASE 10 ->] result.model_dump() se enviara como contexto a Gemini API.
"""

from typing import AsyncGenerator

import anyio
from loguru import logger

from pycommute.core.history import ConsultaHistory
from pycommute.core.models import CommuteResult, ConsultaEntry, RouteData, WeatherData
from pycommute.core.ports import CachePort, RoutePort, WeatherPort


class CommuteService:
    """Servicio principal de PyCommute.

    Recibe los adaptadores por inyeccion de dependencias —
    no sabe si consulta OpenWeather, un mock o cualquier otra fuente.
    La logica de negocio esta aqui; las implementaciones concretas,
    en los adaptadores.
    """

    def __init__(
        self,
        weather: WeatherPort,
        route: RoutePort,
        cache: CachePort,
        history: ConsultaHistory | None = None,
    ) -> None:
        """Inicializa el servicio con sus dependencias.

        Args:
            weather: Adaptador de clima (implementa WeatherPort).
            route: Adaptador de rutas (implementa RoutePort).
            cache: Adaptador de coordenadas (implementa CachePort).
            history: Historial de consultas. Si None, crea uno nuevo.
        """
        self._weather = weather
        self._route = route
        self._cache = cache
        self._history = history or ConsultaHistory()

    async def get_commute_info(
        self,
        city: str,
        destination_city: str,
        profiles: list[str],
        weather_key: str,
        route_key: str,
    ) -> CommuteResult:
        """Obtiene clima y rutas en paralelo, devuelve CommuteResult validado.

        Resuelve las coordenadas via cache, lanza las consultas en paralelo
        con anyio, y construye un CommuteResult — Pydantic calcula best_route
        automaticamente en el model_validator.

        Args:
            city: Ciudad de origen (nombre, ej. "Valencia").
            destination_city: Ciudad de destino (nombre, ej. "Madrid").
            profiles: Perfiles de ruta a consultar.
            weather_key: API key de OpenWeather.
            route_key: API key de OpenRouteService.

        Returns:
            CommuteResult validado con weather, routes y best_route.
        """
        origin = self._cache.get_coordinates(city)
        destination = self._cache.get_coordinates(destination_city)

        weather_data: WeatherData | None = None
        route_list: list[RouteData] = []

        async def fetch_weather() -> None:
            nonlocal weather_data
            weather_data = await self._weather.get_current_weather(city, weather_key)

        async def fetch_routes() -> None:
            async for route in self._iter_routes(
                origin, destination, profiles, route_key
            ):
                route_list.append(route)

        logger.info("Iniciando consultas en paralelo...")
        async with anyio.create_task_group() as tg:
            tg.start_soon(fetch_weather)
            tg.start_soon(fetch_routes)

        result = CommuteResult(weather=weather_data, routes=route_list)

        self._history.add(
            ConsultaEntry(city=city, profiles=profiles, result=result)
        )

        return result

    async def _iter_routes(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        profiles: list[str],
        api_key: str,
    ) -> AsyncGenerator[RouteData, None]:
        """Genera rutas de forma lazy — una por perfil."""
        for profile in profiles:
            yield await self._route.get_route(origin, destination, profile, api_key)

    @property
    def history(self) -> ConsultaHistory:
        """Acceso al historial de consultas."""
        return self._history
