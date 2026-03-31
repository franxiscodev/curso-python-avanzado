"""Adaptador de cache en memoria — implementa CachePort.

# [CLASE 8] cache.py se mueve a adapters/ y se envuelve en MemoryCacheAdapter.
# lru_cache permanece a nivel de modulo para que cache_clear()/cache_info()
# sean accesibles desde los tests sin parchear.
# [CLASE 9 ->] Las coordenadas podrian validarse con un modelo Pydantic.
"""

from functools import lru_cache

from loguru import logger

from pycommute.core.ports import CachePort  # noqa: F401 — cumple el protocolo

_COORDENADAS: dict[str, tuple[float, float]] = {
    "Valencia": (39.4699, -0.3763),
    "Madrid": (40.4168, -3.7038),
    "Barcelona": (41.3851, 2.1734),
    "Sevilla": (37.3891, -5.9845),
    "Bilbao": (43.2630, -2.9350),
}


@lru_cache(maxsize=128)
def get_coordinates(city: str) -> tuple[float, float]:
    """Obtiene las coordenadas de una ciudad con cache en memoria.

    Función de módulo con lru_cache — el adaptador delega a esta función
    para que cache_info() y cache_clear() sean accesibles sin estado de instancia.

    Args:
        city: Nombre de la ciudad.

    Returns:
        Tupla (latitud, longitud).

    Raises:
        ValueError: Si la ciudad no está en el registro.
    """
    city_normalized = city.strip().title()

    if city_normalized not in _COORDENADAS:
        logger.warning("Cache miss — ciudad desconocida: {city}", city=city_normalized)
        raise ValueError(f"Ciudad no encontrada: {city_normalized}")

    coords = _COORDENADAS[city_normalized]
    logger.debug(
        "Cache miss — coordenadas {city}: {coords}",
        city=city_normalized,
        coords=coords,
    )
    return coords


def cache_info() -> str:
    """Devuelve estadísticas del cache de coordenadas."""
    info = get_coordinates.cache_info()
    return (
        f"hits={info.hits}, misses={info.misses}, "
        f"maxsize={info.maxsize}, currsize={info.currsize}"
    )


class MemoryCacheAdapter:
    """Adaptador de cache en memoria con lru_cache.

    Implementa CachePort — si mañana usamos Redis,
    solo cambia este adaptador sin tocar CommuteService.
    """

    def get_coordinates(self, city: str) -> tuple[float, float]:
        """Obtiene las coordenadas de una ciudad.

        Delega a la función get_coordinates() del módulo para
        mantener el cache compartido entre instancias del adaptador.

        Args:
            city: Nombre de la ciudad.

        Returns:
            Tupla (latitud, longitud).

        Raises:
            ValueError: Si la ciudad no está en el registro.
        """
        return get_coordinates(city)
