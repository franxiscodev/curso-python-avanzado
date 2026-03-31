"""Puertos de PyCommute — contratos definidos con typing.Protocol.

# [CLASE 8] Introduccion de Arquitectura Hexagonal.
# Antes (Clase 7): no existia este archivo. Las dependencias de commute.py
# eran importaciones directas de weather.py, route.py, cache.py.
# [CLASE 9 ->] Los puertos se mantienen; se agregan modelos Pydantic
# para validar los datos que entran y salen de los adaptadores.

Un puerto define QUE hace un componente, no COMO lo hace.
Cualquier clase que implemente estos metodos cumple el contrato
sin necesidad de heredar — eso es duck typing estructural.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class WeatherPort(Protocol):
    """Puerto para consultar datos de clima."""

    async def get_current_weather(
        self, city: str, api_key: str
    ) -> dict[str, Any]:
        """Obtiene el clima actual para una ciudad.

        Args:
            city: Nombre de la ciudad.
            api_key: Clave de autenticación.

        Returns:
            Dict con temperature, description, city.
        """
        ...


@runtime_checkable
class RoutePort(Protocol):
    """Puerto para consultar rutas entre dos puntos."""

    async def get_route(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        profile: str,
        api_key: str,
    ) -> dict[str, Any]:
        """Obtiene una ruta entre dos coordenadas.

        Args:
            origin: Coordenadas de origen (lat, lon).
            destination: Coordenadas de destino (lat, lon).
            profile: Perfil de transporte.
            api_key: Clave de autenticación.

        Returns:
            Dict con distance_km, duration_min, profile.
        """
        ...


@runtime_checkable
class CachePort(Protocol):
    """Puerto para obtener coordenadas de ciudades."""

    def get_coordinates(self, city: str) -> tuple[float, float]:
        """Obtiene las coordenadas de una ciudad.

        Args:
            city: Nombre de la ciudad.

        Returns:
            Tupla (latitud, longitud).

        Raises:
            ValueError: Si la ciudad no está disponible.
        """
        ...
