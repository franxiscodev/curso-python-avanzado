"""Servicio de movilidad — orquesta usando puertos inyectados.

# [CLASE 8] get_commute_info pasa de funcion libre a metodo de CommuteService.
# Antes (Clase 7): get_commute_info(city, origin, destination, profiles, ...)
#   importaba directamente get_current_weather y get_route.
# Ahora: CommuteService recibe weather, route y cache por constructor (DI).
# [CLASE 9 ->] Los dicts retornados se reemplazaran por modelos Pydantic.
"""

from typing import Any, AsyncGenerator

import anyio
from loguru import logger

from pycommute.core.history import ConsultaHistory
from pycommute.core.ports import CachePort, RoutePort, WeatherPort
from pycommute.core.ranking import rank_routes_by_time


class CommuteService:
    """Servicio principal de PyCommute.

    Recibe los adaptadores por inyección de dependencias —
    no sabe si consulta OpenWeather, un mock o cualquier otra fuente.
    La lógica de negocio está aquí; las implementaciones concretas,
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
    ) -> dict[str, Any]:
        """Obtiene clima y rutas en paralelo con ranking automático.

        Resuelve las coordenadas via cache, lanza las consultas en paralelo
        con anyio, rankea las rutas por tiempo y registra en el historial.

        Args:
            city: Ciudad de origen (nombre, ej. "Valencia").
            destination_city: Ciudad de destino (nombre, ej. "Madrid").
            profiles: Perfiles de ruta a consultar.
            weather_key: API key de OpenWeather.
            route_key: API key de OpenRouteService.

        Returns:
            Diccionario con:
                - weather (dict): resultado de clima.
                - routes (list[dict]): rutas rankeadas por tiempo.
        """
        origin = self._cache.get_coordinates(city)
        destination = self._cache.get_coordinates(destination_city)

        results: dict[str, Any] = {}

        async def fetch_weather() -> None:
            results["weather"] = await self._weather.get_current_weather(
                city, weather_key
            )

        async def fetch_routes() -> None:
            routes = []
            async for route in self._iter_routes(
                origin, destination, profiles, route_key
            ):
                routes.append(route)
            results["routes"] = rank_routes_by_time(routes)

        logger.info("Iniciando consultas en paralelo...")
        async with anyio.create_task_group() as tg:
            tg.start_soon(fetch_weather)
            tg.start_soon(fetch_routes)

        self._history.add(
            city=city,
            profiles=profiles,
            weather=results["weather"],
            routes=results["routes"],
        )

        return results

    async def _iter_routes(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        profiles: list[str],
        api_key: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Genera rutas de forma lazy — una por perfil."""
        for profile in profiles:
            yield await self._route.get_route(origin, destination, profile, api_key)

    @property
    def history(self) -> ConsultaHistory:
        """Acceso al historial de consultas."""
        return self._history
