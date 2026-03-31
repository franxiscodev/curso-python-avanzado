"""Ranking de rutas por prioridad usando heapq.

heapq mantiene una lista ordenada con inserción O(log n)
en lugar de ordenar toda la lista en cada operación O(n log n).
"""

# [CLASE 7] Módulo nuevo — introduce heapq como estructura de datos especializada.
# Por qué heapq y no sorted(): sorted() reconstruye el orden completo cada vez.
# heappush/heappop es O(log n) por operación — clave cuando llegan rutas en tiempo real.
# Patrón central: tupla (prioridad, índice, dato) para ordenar objetos no comparables.
#
# [CLASE 8 →] ranking.py se convertirá en un servicio del sistema hexagonal.
#             Recibirá un puerto RankingPort en lugar de implementar la lógica directamente.

import heapq
from typing import Any

from loguru import logger


def rank_routes_by_time(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rankea rutas de menor a mayor tiempo usando un min-heap.

    Args:
        routes: Lista de dicts con duration_min, distance_km y profile.

    Returns:
        Lista ordenada de rutas — la más rápida primero.
    """
    if not routes:
        return []

    # [CLASE 7] Patrón (prioridad, índice, dato):
    # - prioridad: clave de ordenamiento (duration_min)
    # - índice: desempate determinista — evita comparar dicts con '<'
    # - dato: el dict completo para recuperar después del pop
    heap: list[tuple[float, int, dict[str, Any]]] = []
    for i, route in enumerate(routes):
        heapq.heappush(heap, (route["duration_min"], i, route))

    ranked = []
    while heap:
        _, _, route = heapq.heappop(heap)
        ranked.append(route)

    logger.debug(
        "Rutas rankeadas: {n} rutas, mejor tiempo: {best} min",
        n=len(ranked),
        best=ranked[0]["duration_min"] if ranked else 0,
    )
    return ranked


def rank_routes_by_distance(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rankea rutas de menor a mayor distancia usando un min-heap.

    Args:
        routes: Lista de dicts con duration_min, distance_km y profile.

    Returns:
        Lista ordenada de rutas — la más corta primero.
    """
    if not routes:
        return []

    heap: list[tuple[float, int, dict[str, Any]]] = []
    for i, route in enumerate(routes):
        heapq.heappush(heap, (route["distance_km"], i, route))

    ranked = []
    while heap:
        _, _, route = heapq.heappop(heap)
        ranked.append(route)

    return ranked


# [CLASE 7] get_best_route usa heapq.nsmallest(1, ...) — O(n).
# sorted()[0] sería O(n log n). Para obtener solo el mínimo, nsmallest es mejor.
def get_best_route(routes: list[dict[str, Any]], by: str = "time") -> dict[str, Any]:
    """Obtiene la mejor ruta según criterio sin ordenar toda la lista.

    Usa heapq.nsmallest — O(n) en lugar de O(n log n) para obtener solo 1.

    Args:
        routes: Lista de rutas.
        by: Criterio — "time" o "distance".

    Returns:
        La ruta con menor tiempo o distancia.

    Raises:
        ValueError: Si routes está vacía o by es inválido.
    """
    if not routes:
        raise ValueError("No hay rutas para rankear")

    key_map = {"time": "duration_min", "distance": "distance_km"}
    if by not in key_map:
        raise ValueError(f"Criterio inválido: {by}. Usar 'time' o 'distance'")

    key = key_map[by]
    best = heapq.nsmallest(1, routes, key=lambda r: r[key])[0]
    logger.info(
        "Mejor ruta ({by}): {profile} — {val}",
        by=by,
        profile=best["profile"],
        val=best[key],
    )
    return best
