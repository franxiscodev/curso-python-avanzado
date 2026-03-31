"""deque basico — cola doble eficiente con maxlen.

Demuestra append/pop desde ambos extremos en O(1) y el
comportamiento de descarte automatico con maxlen.
Sin imports de pycommute.

Ejecutar:
    uv run scripts/clase_07/conceptos/03_deque_basico.py
"""

from collections import deque

# ── deque basico — ambos extremos ────────────────────────────────
d: deque[str] = deque()
d.append("C")       # agrega a la derecha
d.appendleft("A")   # agrega a la izquierda
d.append("D")
d.appendleft("inicio")

print(f"deque: {list(d)}")
print(f"pop():      {d.pop()}     <- extrae del lado derecho")
print(f"popleft():  {d.popleft()}  <- extrae del lado izquierdo")
print(f"despues:    {list(d)}")

# ── deque con maxlen — descarte automatico ────────────────────────
print("\ndeque con maxlen=3 (historial de ultimas 3 consultas):")
historial: deque[str] = deque(maxlen=3)
ciudades = ["Valencia", "Madrid", "Barcelona", "Sevilla", "Bilbao"]

for ciudad in ciudades:
    historial.append(ciudad)
    print(f"  append({ciudad:<12}) -> {list(historial)}")

print(f"\nSolo se conservan las ultimas {historial.maxlen} consultas.")
print(f"Valencia y Madrid fueron descartadas automaticamente.")

# ── Otros metodos utiles ──────────────────────────────────────────
print("\nOtros metodos:")
d2: deque[int] = deque([1, 2, 3, 4, 5])
print(f"  original:      {list(d2)}")
d2.rotate(2)   # mueve los ultimos 2 elementos al principio
print(f"  rotate(2):     {list(d2)}")
d2.rotate(-2)  # deshace
print(f"  rotate(-2):    {list(d2)}")
print(f"  [0]:           {d2[0]}  (acceso por indice O(1) en extremos, O(n) en medio)")
