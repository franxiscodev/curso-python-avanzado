"""Benchmark comparativo — lista vs generador vs lru_cache.

Compara el impacto en memoria y velocidad de las tres técnicas
vistas en Clase 6. Sin imports de pycommute.

Ejecutar:
    uv run scripts/clase_06/conceptos/04_benchmark_comparativo.py
"""

import time
from functools import lru_cache
from typing import Generator


N = 1_000  # valores unicos — maxsize debe cubrir todos para ver hits reales


# ── Escenario 1: Sin optimización ───────────────────────────────
def calcular_sin_optimizar(items: list[int]) -> list[float]:
    """Construye la lista completa antes de retornar."""
    resultados = []
    for item in items:
        resultados.append(item**0.5)
    return resultados


# ── Escenario 2: Con generador ───────────────────────────────────
def calcular_con_generador(items: list[int]) -> Generator[float, None, None]:
    """Genera resultados de uno en uno bajo demanda."""
    for item in items:
        yield item**0.5


# ── Escenario 3: Con lru_cache para valores repetidos ────────────
# maxsize >= N para que todos los valores quepan y haya hits reales
@lru_cache(maxsize=N)
def raiz_cacheada(n: int) -> float:
    """Calcula la raiz cuadrada con cache."""
    return n**0.5


def calcular_con_cache(items: list[int]) -> list[float]:
    """Usa lru_cache para evitar recalcular valores repetidos."""
    return [raiz_cacheada(item) for item in items]


# ── Benchmark con datos únicos ───────────────────────────────────
datos = list(range(N))
datos_con_repeticion = datos * 3  # 3000 items, 1000 unicos

print(f"Procesando {N} items unicos:")

t = time.perf_counter()
r1 = calcular_sin_optimizar(datos)
print(f"  Sin optimizar:   {time.perf_counter() - t:.5f}s  ({len(r1)} resultados en RAM)")

t = time.perf_counter()
r2 = list(calcular_con_generador(datos))
print(f"  Con generador:   {time.perf_counter() - t:.5f}s  (construido lazy, mismo resultado)")

print()
print(f"Procesando {len(datos_con_repeticion)} items con repeticion (x3):")

t = time.perf_counter()
r3 = calcular_sin_optimizar(datos_con_repeticion)
print(f"  Sin cache:       {time.perf_counter() - t:.5f}s  (recalcula duplicados)")

raiz_cacheada.cache_clear()  # asegurar benchmark limpio
t = time.perf_counter()
r4 = calcular_con_cache(datos_con_repeticion)
tiempo_cache = time.perf_counter() - t
print(f"  Con lru_cache:   {tiempo_cache:.5f}s  (cache hits en duplicados)")
info = raiz_cacheada.cache_info()
print(f"  Cache stats:     hits={info.hits}, misses={info.misses}, currsize={info.currsize}")
print()
print("Conclusión:")
print("  - Generadores ahorran memoria cuando procesas de forma lazy")
print("  - lru_cache gana velocidad cuando hay valores que se repiten")
print("  - Combinar ambos es posible (y potente)")
