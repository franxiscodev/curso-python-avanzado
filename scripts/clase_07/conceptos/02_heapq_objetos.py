"""heapq con objetos — patron (prioridad, indice, dato).

heapq compara elementos con '<'. Los dicts y objetos no son
comparables por defecto — se usan tuplas donde el primer elemento
es la clave de ordenamiento. Sin imports de pycommute.

Ejecutar:
    uv run scripts/clase_07/conceptos/02_heapq_objetos.py
"""

import heapq
from dataclasses import dataclass


@dataclass
class Tarea:
    """Tarea con prioridad (1 = mas urgente)."""

    nombre: str
    prioridad: int
    duracion: float


tareas = [
    Tarea("Revisar email", 3, 0.5),
    Tarea("Reunion urgente", 1, 1.0),
    Tarea("Documentar codigo", 4, 2.0),
    Tarea("Fix bug critico", 1, 0.5),  # empate de prioridad con Reunion
    Tarea("Code review", 2, 1.5),
]

# ── Patron: (prioridad, indice, objeto) ──────────────────────────
# El indice rompe empates — sin el, Python intentaria comparar Tarea
# con Tarea y fallaria con TypeError.
heap: list[tuple[int, int, Tarea]] = []
for i, tarea in enumerate(tareas):
    heapq.heappush(heap, (tarea.prioridad, i, tarea))

print("Tareas por prioridad (1 = mas urgente):")
while heap:
    prioridad, indice, tarea = heapq.heappop(heap)
    print(f"  [{prioridad}] {tarea.nombre:<25} ({tarea.duracion}h)")

print()
print("Por que el indice como desempate?")
print("  Si dos tareas tienen la misma prioridad, Python compara el segundo")
print("  elemento de la tupla (el indice). Como los indices son unicos,")
print("  nunca llega a comparar el tercer elemento (Tarea).")
print()
print("  Sin el indice: TypeError — '<' not supported between Tarea and Tarea")

# ── Demostrar el error ────────────────────────────────────────────
print()
print("Demo del error sin indice:")
heap2: list[tuple[int, Tarea]] = []
try:
    heapq.heappush(heap2, (1, Tarea("Tarea A", 1, 1.0)))
    heapq.heappush(heap2, (1, Tarea("Tarea B", 1, 2.0)))  # mismo prio -> compara Tarea
    heapq.heappop(heap2)
    heapq.heappop(heap2)  # aqui falla
    print("  (sin error en este caso)")
except TypeError as e:
    print(f"  TypeError: {e}")
