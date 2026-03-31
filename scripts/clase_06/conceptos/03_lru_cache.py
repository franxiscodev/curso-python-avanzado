"""lru_cache — cachear resultados costosos.

Demuestra el patrón de memoización con functools.lru_cache usando
fibonacci como ejemplo clásico. Sin imports de pycommute.

Ejecutar:
    uv run scripts/clase_06/conceptos/03_lru_cache.py
"""

import time
from functools import lru_cache


# ── Sin cache — recalcula en cada llamada ────────────────────────
def fibonacci_sin_cache(n: int) -> int:
    """Fibonacci recursivo sin optimización — O(2^n) llamadas."""
    if n < 2:
        return n
    return fibonacci_sin_cache(n - 1) + fibonacci_sin_cache(n - 2)


# ── Con cache — cada resultado se recuerda ───────────────────────
@lru_cache(maxsize=128)
def fibonacci_con_cache(n: int) -> int:
    """Fibonacci recursivo con memoización — O(n) llamadas únicas."""
    if n < 2:
        return n
    return fibonacci_con_cache(n - 1) + fibonacci_con_cache(n - 2)


# ── Benchmark ────────────────────────────────────────────────────
N = 35

inicio = time.perf_counter()
resultado_sin = fibonacci_sin_cache(N)
tiempo_sin = time.perf_counter() - inicio

inicio = time.perf_counter()
resultado_con = fibonacci_con_cache(N)
tiempo_con = time.perf_counter() - inicio

print(f"fibonacci({N}) = {resultado_sin}")
print()
print(f"Sin cache:  {tiempo_sin:.4f}s")
print(f"Con cache:  {tiempo_con:.6f}s")
if tiempo_con > 0:
    print(f"Mejora:     {tiempo_sin / tiempo_con:.0f}x más rápido")
print()

# ── Estadísticas del cache ───────────────────────────────────────
info = fibonacci_con_cache.cache_info()
print(f"cache_info():")
print(f"  hits     = {info.hits}     (llamadas resueltas desde cache)")
print(f"  misses   = {info.misses}     (llamadas que requirieron calculo)")
print(f"  maxsize  = {info.maxsize}   (entradas maximas en cache)")
print(f"  currsize = {info.currsize}     (entradas actuales)")
print()

# ── Limpiar cache ────────────────────────────────────────────────
fibonacci_con_cache.cache_clear()
info_limpio = fibonacci_con_cache.cache_info()
print(f"Tras cache_clear(): hits={info_limpio.hits}, currsize={info_limpio.currsize}")
print()
print("Limitaciones de lru_cache:")
print("  [NO] Solo funciona con argumentos hashables (no listas, no dicts)")
print("  [NO] No expira automaticamente (TTL) -- cache permanente en proceso")
print("  [NO] No se comparte entre procesos (no distribuido)")
print("  [SI] Thread-safe en CPython")
