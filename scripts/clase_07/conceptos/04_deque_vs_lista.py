"""deque vs lista — benchmark pop(0) vs popleft().

Demuestra que list.pop(0) es O(n) mientras que deque.popleft()
es O(1). La diferencia se hace evidente con N grande.
Sin imports de pycommute.

Ejecutar:
    uv run scripts/clase_07/conceptos/04_deque_vs_lista.py
"""

import time
from collections import deque

N = 100_000
MAXLEN = 100

# ── Con lista — pop(0) es O(n) ────────────────────────────────────
lista: list[int] = []
inicio = time.perf_counter()
for i in range(N):
    lista.append(i)
    if len(lista) > MAXLEN:
        lista.pop(0)   # O(n) — desplaza todos los elementos a la izquierda
tiempo_lista = time.perf_counter() - inicio

# ── Con deque — maxlen automatico, O(1) ──────────────────────────
d: deque[int] = deque(maxlen=MAXLEN)
inicio = time.perf_counter()
for i in range(N):
    d.append(i)        # O(1) — descarta automaticamente si lleno
tiempo_deque = time.perf_counter() - inicio

print(f"Mantener solo las ultimas {MAXLEN} entradas de {N} inserciones:")
print()
print(f"  list + pop(0):          {tiempo_lista:.4f}s")
print(f"  deque(maxlen={MAXLEN}):       {tiempo_deque:.4f}s")
if tiempo_deque > 0:
    print(f"  Mejora:                 {tiempo_lista / tiempo_deque:.0f}x mas rapido")
print()
print(f"Ambos tienen {MAXLEN} items al final:")
print(f"  lista[-3:] = {lista[-3:]}")
print(f"  deque[-3:] = {list(d)[-3:]}")
print()
print("Complejidades:")
print("  list.append():  O(1) amortizado")
print("  list.pop(0):    O(n) -- mueve N elementos")
print("  deque.append(): O(1)")
print("  deque.popleft():O(1) -- lista doblemente enlazada")
print()
print("Regla: si necesitas extraer del principio frecuentemente, usa deque.")
