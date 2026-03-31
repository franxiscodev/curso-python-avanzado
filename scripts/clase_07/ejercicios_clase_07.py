"""
Ejercicios — Clase 07: Algoritmia Eficiente con heapq y deque
=============================================================
Cuatro ejercicios sobre heapq, deque y combinaciones de ambos.

Ejecutar (desde curso/):
    uv run python scripts/clase_07/ejercicios_clase_07.py

Requisito: autocontenido, sin imports de pycommute.
"""

import heapq
from collections import deque
from typing import Any


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — heappush/heappop para encontrar los N menores elementos
# Implementa `n_menores` que:
#   - Recibe una lista de números `valores: list[float]` y un entero `n: int`
#   - Retorna una lista con los `n` menores valores en orden ascendente
#   - Usa heapq.heappush y heapq.heappop (NO uses sorted() ni heapq.nsmallest)
# Ejemplo: n_menores([5, 2, 8, 1, 9, 3], 3) → [1, 2, 3]
# Pista: repasa "heapq — cola de prioridad" en 01_conceptos.md
def n_menores(valores: list[float], n: int) -> list[float]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — deque con maxlen como historial deslizante
# Implementa `historial_deslizante` que:
#   - Recibe una lista de items y un entero `maxlen: int`
#   - Crea un deque con maxlen=maxlen
#   - Añade TODOS los items de la lista al deque uno por uno (appendleft NO)
#   - Retorna el deque resultante (que conservará solo los últimos maxlen items)
# Ejemplo: historial_deslizante(range(10), maxlen=5)
#          → deque([5, 6, 7, 8, 9], maxlen=5)
# Pista: repasa "collections.deque — cola de doble extremo" en 01_conceptos.md
def historial_deslizante(items, maxlen: int) -> deque:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — Cola de prioridad con heapq usando tuplas
# Implementa `ColaprioridAd` como una clase con:
#   - `__init__`: inicializa una lista interna `_heap: list`
#   - `insertar(self, prioridad: int, item: Any) -> None`:
#       inserta la tupla (prioridad, item) con heapq.heappush
#   - `extraer(self) -> tuple[int, Any]`:
#       extrae y retorna la tupla con menor prioridad con heapq.heappop
#   - `esta_vacia(self) -> bool`:
#       retorna True si el heap está vacío
# Uso esperado:
#   cola = ColaPrioridad()
#   cola.insertar(3, "bajo")
#   cola.insertar(1, "urgente")
#   cola.insertar(2, "normal")
#   cola.extraer()  → (1, "urgente")
# Pista: repasa "Cola de prioridad con tuplas" en 01_conceptos.md
class ColaPrioridad:
    def __init__(self) -> None:
        pass  # ← reemplazar con tu implementación

    def insertar(self, prioridad: int, item: Any) -> None:
        pass  # ← reemplazar con tu implementación

    def extraer(self) -> tuple[int, Any]:
        pass  # ← reemplazar con tu implementación

    def esta_vacia(self) -> bool:
        pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 4
# ---------------------------------------------------------------------------

# TODO: Ejercicio 4 — Combinar deque y heapq: historial de mejores N resultados
# Implementa `mejores_n_historial` que:
#   - Recibe una lista de puntuaciones (float) y un entero `n: int`
#   - Procesa las puntuaciones UNA por una (simula stream de datos)
#   - Para cada nueva puntuación, la añade a un historial deque (sin maxlen)
#   - Al final, usa heapq.nlargest para retornar las n mejores puntuaciones
#     ordenadas de mayor a menor
# Ejemplo: mejores_n_historial([3.0, 8.5, 1.2, 9.1, 4.7, 6.0], n=3)
#          → [9.1, 8.5, 6.0]
# Pista: combina deque (historial completo) con heapq.nlargest (top N)
def mejores_n_historial(puntuaciones: list[float], n: int) -> list[float]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo() -> None:
    print("=== Ejercicio 1: n_menores ===")
    datos = [5.0, 2.0, 8.0, 1.0, 9.0, 3.0, 7.0]
    resultado = n_menores(datos, 3)
    if resultado is not None:
        print(f"  {datos} → 3 menores: {resultado}")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 2: historial_deslizante ===")
    hist = historial_deslizante(range(10), maxlen=5)
    if hist is not None:
        print(f"  range(10) con maxlen=5 → {hist}")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 3: ColaPrioridad ===")
    cola = ColaPrioridad()
    if cola.esta_vacia() is not None:
        cola.insertar(3, "bajo")
        cola.insertar(1, "urgente")
        cola.insertar(2, "normal")
        while not cola.esta_vacia():
            print(f"  extraído: {cola.extraer()}")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 4: mejores_n_historial ===")
    puntuaciones = [3.0, 8.5, 1.2, 9.1, 4.7, 6.0]
    top3 = mejores_n_historial(puntuaciones, n=3)
    if top3 is not None:
        print(f"  puntuaciones: {puntuaciones}")
        print(f"  top 3: {top3}")
    else:
        print("Sin implementar aún.")


if __name__ == "__main__":
    demo()
