"""heapq basico — cola de prioridad con min-heap.

Demuestra la propiedad fundamental: el minimo siempre esta en heap[0],
sin importar el orden de insercion. Sin imports de pycommute.

Ejecutar:
    uv run scripts/clase_07/conceptos/01_heapq_basico.py
"""

import heapq

# ── Min-heap — el minimo siempre en heap[0] ──────────────────────
numeros = [5, 2, 8, 1, 9, 3]
heap: list[int] = []

print("Insertando uno por uno:")
for n in numeros:
    heapq.heappush(heap, n)
    print(f"  heappush({n}) -> heap[0] = {heap[0]}  (siempre el minimo)")

print("\nExtrayendo en orden:")
while heap:
    print(f"  heappop() -> {heapq.heappop(heap)}")

# ── heapify — convertir lista existente en heap O(n) ─────────────
print("\nheapify sobre lista existente (O(n)):")
datos = [5, 2, 8, 1, 9, 3]
heapq.heapify(datos)
print(f"  antes: [5, 2, 8, 1, 9, 3]")
print(f"  despues: {datos}")
print(f"  datos[0] = {datos[0]}  (el minimo, garantizado)")

# ── nsmallest y nlargest ─────────────────────────────────────────
print("\nnsmallest y nlargest:")
valores = [5, 2, 8, 1, 9, 3, 7, 4, 6]
print(f"  nsmallest(3): {heapq.nsmallest(3, valores)}  O(n) para k pequeno")
print(f"  nlargest(3):  {heapq.nlargest(3, valores)}   O(n) para k pequeno")
print()
print("Cuando usar cada uno:")
print("  heappush/heappop: inserciones frecuentes, siempre el minimo")
print("  nsmallest(1):     obtener el minimo una sola vez, sin modificar la lista")
print("  sorted():         cuando necesitas la lista completa ordenada")
