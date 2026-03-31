"""Cache de coordenadas geográficas para PyCommute.

Evita llamadas repetidas a la API de geocodificación
cacheando resultados en memoria con lru_cache.
"""

# [CLASE 6] Módulo nuevo — introduce lru_cache para memoización de coordenadas.
# El patrón: registrar el costo de la primera llamada, reutilizar las siguientes.
# En producción, _COORDENADAS vendría de una API de geocodificación.
# [CLASE 8 →] cache.py puede convertirse en un puerto del sistema hexagonal,
#             con adaptador que hable con una API real o Redis.

from functools import lru_cache

from loguru import logger


# Coordenadas hardcodeadas para las ciudades más usadas en el curso.
# En producción esto vendría de una API de geocodificación.
_COORDENADAS: dict[str, tuple[float, float]] = {
    "Valencia": (39.4699, -0.3763),
    "Madrid": (40.4168, -3.7038),
    "Barcelona": (41.3851, 2.1734),
    "Sevilla": (37.3891, -5.9845),
    "Bilbao": (43.2630, -2.9350),
}


# [CLASE 6] @lru_cache convierte la función en memoizada.
# Primera llamada con city="Valencia": ejecuta el cuerpo (cache miss).
# Segunda llamada con city="Valencia": retorna desde cache (cache hit, cero cómputo).
# Limitación: solo funciona con argumentos hashables (str, int, tuple — no listas).
@lru_cache(maxsize=128)
def get_coordinates(city: str) -> tuple[float, float]:
    """Obtiene las coordenadas de una ciudad con cache en memoria.

    La primera llamada realiza la búsqueda en el registro interno.
    Las llamadas siguientes con el mismo argumento retornan el resultado
    cacheado sin ningún cálculo adicional.

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


# [CLASE 6] cache_info() es una función de introspección expuesta por lru_cache.
# Permite observar hits/misses en tiempo de ejecución — útil para profiling.
def cache_info() -> str:
    """Devuelve estadísticas del cache de coordenadas.

    Returns:
        String con hits, misses, maxsize y currsize del cache.
    """
    info = get_coordinates.cache_info()
    return (
        f"hits={info.hits}, misses={info.misses}, "
        f"maxsize={info.maxsize}, currsize={info.currsize}"
    )
