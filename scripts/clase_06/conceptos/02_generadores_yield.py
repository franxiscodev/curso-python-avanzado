"""Generadores con yield — procesamiento lazy.

Demuestra la diferencia entre listas (todo en memoria) y generadores
(un elemento a la vez). Sin imports de pycommute.

Ejecutar:
    uv run scripts/clase_06/conceptos/02_generadores_yield.py
"""

import sys
from typing import Generator


# ── Lista completa — todo en memoria antes de empezar ───────────
def numeros_lista(n: int) -> list[int]:
    """Construye todos los cuadrados antes de retornar."""
    return [i * i for i in range(n)]


# ── Generador — uno por uno, lazy ───────────────────────────────
def numeros_generador(n: int) -> Generator[int, None, None]:
    """Genera cuadrados de uno en uno bajo demanda."""
    for i in range(n):
        yield i * i  # pausa aquí hasta que el consumidor pida el siguiente


# ── Comparar tamaño en memoria ───────────────────────────────────
N = 1000
lista = numeros_lista(N)
gen = numeros_generador(N)

print(f"Lista ({N} items):   {sys.getsizeof(lista):>8} bytes")
print(f"Generador:          {sys.getsizeof(gen):>8} bytes")
print(f"Factor:             {sys.getsizeof(lista) // sys.getsizeof(gen)}x más memoria en lista")
print()

# ── Consumir parcialmente el generador ───────────────────────────
print("Primeros 3 valores del generador (el resto NO se calcula):")
for i, val in enumerate(numeros_generador(N)):
    print(f"  cuadrado({i}) = {val}")
    if i >= 2:
        break
print("  ... (se detuvo aqui -- Python no calculo los 997 restantes)")
print()

# ── Generator expression — sintaxis compacta ─────────────────────
cuadrados_gen = (i * i for i in range(10))  # nota: () no []
cuadrados_lista = [i * i for i in range(10)]  # [] crea lista

print(f"Generator expression: {type(cuadrados_gen)}")
print(f"List comprehension:   {type(cuadrados_lista)}")
print()
print("Cuando usar generadores:")
print("  [SI] Procesar elementos de uno en uno")
print("  [SI] Dataset muy grande que no cabe en RAM")
print("  [SI] Pipeline de transformaciones")
print("  [NO] Necesitas acceso aleatorio (lista[5])")
print("  [NO] Necesitas saber el total antes de empezar")
print("  [NO] Necesitas iterar mas de una vez")
