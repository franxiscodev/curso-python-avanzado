"""
Ejercicios — Clase 06: Eficiencia y Profiling
==============================================
Cuatro ejercicios sobre generadores, lru_cache y comparación de tiempos.

Ejecutar (desde curso/):
    uv run python scripts/clase_06/ejercicios_clase_06.py

Requisito: autocontenido, sin imports de pycommute.
"""

import time
from functools import lru_cache
from typing import Generator, Iterator


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Generador de números de Fibonacci
# Implementa `fibonacci_gen` que:
#   - Es una función generadora (usa `yield`)
#   - Recibe `n: int` — cuántos números producir
#   - Produce los primeros n números de Fibonacci: 0, 1, 1, 2, 3, 5, 8, ...
#   - Retorna un Generator[int, None, None]
# Ejemplo: list(fibonacci_gen(7)) → [0, 1, 1, 2, 3, 5, 8]
# Pista: repasa "Generadores con yield" en 01_conceptos.md
def fibonacci_gen(n: int) -> Generator[int, None, None]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — lru_cache en función recursiva
# Implementa `factorial_cached` que:
#   - Está decorada con @lru_cache(maxsize=128)
#   - Calcula el factorial de n de forma recursiva
#   - factorial_cached(0) == 1, factorial_cached(1) == 1
#   - Para n > 1: factorial_cached(n) == n * factorial_cached(n - 1)
# Pista: repasa "functools.lru_cache" en 01_conceptos.md
@lru_cache(maxsize=128)
def factorial_cached(n: int) -> int:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — Generador con yield from para aplanar listas anidadas
# Implementa `aplanar` que:
#   - Es una función generadora
#   - Recibe una lista que puede contener sublistas (un nivel de anidamiento)
#   - Produce cada elemento de cada sublista (o elemento directo si no es lista)
#   - Usa `yield from` para delegar en sublistas
# Ejemplo: list(aplanar([1, [2, 3], 4, [5, 6]])) → [1, 2, 3, 4, 5, 6]
# Pista: repasa "yield from — delegación de generadores" en 01_conceptos.md
def aplanar(items: list) -> Generator:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 4
# ---------------------------------------------------------------------------

# Función lenta sin caché (ya implementada — no modificar)
def fibonacci_lento(n: int) -> int:
    """Calcula el n-ésimo número de Fibonacci de forma recursiva SIN caché."""
    if n <= 1:
        return n
    return fibonacci_lento(n - 1) + fibonacci_lento(n - 2)


# TODO: Ejercicio 4 — Comparar tiempo con/sin lru_cache
# Implementa `fibonacci_rapido` que:
#   - Está decorada con @lru_cache(maxsize=None)
#   - Calcula el n-ésimo número de Fibonacci de forma recursiva
#   - Tiene la misma lógica que fibonacci_lento
#
# Luego implementa `comparar_tiempos` que:
#   - Mide el tiempo de fibonacci_lento(30) con time.perf_counter()
#   - Mide el tiempo de fibonacci_rapido(30) con time.perf_counter()
#   - Imprime ambos tiempos y la diferencia
#   - Retorna una tupla (tiempo_lento: float, tiempo_rapido: float)
# Pista: repasa "Medir tiempo con time.perf_counter()" en 01_conceptos.md
@lru_cache(maxsize=None)
def fibonacci_rapido(n: int) -> int:
    pass  # ← reemplazar con tu implementación


def comparar_tiempos() -> tuple[float, float]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo() -> None:
    print("=== Ejercicio 1: fibonacci_gen ===")
    fibs = list(fibonacci_gen(8))
    if fibs:
        print(f"Primeros 8 Fibonacci: {fibs}")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 2: factorial_cached ===")
    for n in [0, 1, 5, 10]:
        resultado = factorial_cached(n)
        if resultado is not None:
            print(f"  {n}! = {resultado}")
    info = factorial_cached.cache_info()
    print(f"  Cache info: {info}")

    print("\n=== Ejercicio 3: aplanar ===")
    anidada = [1, [2, 3], 4, [5, 6, 7]]
    resultado = list(aplanar(anidada))
    if resultado:
        print(f"  {anidada} → {resultado}")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 4: comparar_tiempos ===")
    tiempos = comparar_tiempos()
    if tiempos:
        lento, rapido = tiempos
        print(f"  fibonacci_lento(30) : {lento:.4f}s")
        print(f"  fibonacci_rapido(30): {rapido:.6f}s")
        if lento > 0 and rapido > 0:
            print(f"  Speedup: x{lento/rapido:.0f}")
    else:
        print("Sin implementar aún.")


if __name__ == "__main__":
    demo()
