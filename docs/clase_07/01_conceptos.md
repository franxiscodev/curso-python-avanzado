# Clase 07 — Conceptos: Algoritmia Eficiente

---

## 1. heapq — cola de prioridad

Un heap es una estructura de datos que garantiza una propiedad: el elemento
mínimo siempre está disponible en O(1), y se puede insertar un nuevo elemento
en O(log n).

Python implementa un **min-heap** a través del módulo `heapq`. La estructura
se almacena como una lista normal, pero con el invariante de que `heap[0]`
siempre es el elemento mínimo.

### Uso básico

```python
import heapq

heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 2)
heapq.heappush(heap, 8)

print(heap[0])           # 2 — siempre el mínimo
print(heapq.heappop(heap))  # 2 — extrae y elimina el mínimo
print(heap[0])           # 5 — nuevo mínimo
```

### heapify — convertir una lista existente

```python
datos = [5, 2, 8, 1, 9, 3]
heapq.heapify(datos)     # O(n) — más eficiente que N heappush()
print(datos[0])          # 1 — el mínimo
```

### nsmallest y nlargest

```python
valores = [5, 2, 8, 1, 9, 3]
print(heapq.nsmallest(3, valores))  # [1, 2, 3]
print(heapq.nlargest(3, valores))   # [9, 8, 5]
```

`nsmallest(1, datos)` es O(n) — más eficiente que `sorted(datos)[0]` que es O(n log n).

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_07/conceptos/01_heapq_basico.py
```

---

## 2. heapq con objetos

`heapq` compara elementos con `<`. Los dicts no implementan `<`, por lo que
se necesita el patrón de tuplas para ordenar objetos personalizados.

### El patrón (prioridad, índice, dato)

```python
from dataclasses import dataclass
import heapq

@dataclass
class Tarea:
    nombre: str
    prioridad: int  # 1 = más urgente

tareas = [Tarea("Email", 3), Tarea("Bug", 1), Tarea("Docs", 2)]

heap: list[tuple[int, int, Tarea]] = []
for i, tarea in enumerate(tareas):
    heapq.heappush(heap, (tarea.prioridad, i, tarea))

while heap:
    _, _, tarea = heapq.heappop(heap)
    print(tarea.nombre)  # Bug, Docs, Email
```

El `índice` (segundo elemento) sirve como desempate cuando dos tareas tienen
la misma prioridad, evitando que Python compare los objetos `Tarea` entre sí.

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_07/conceptos/02_heapq_objetos.py
```

---

## 3. collections.deque — cola doble eficiente

`deque` (double-ended queue) permite agregar y quitar elementos de ambos
extremos en O(1). Es especialmente útil para implementar historiales con
tamaño máximo.

### Uso básico

```python
from collections import deque

d: deque[str] = deque()
d.append("derecha")       # O(1) — agrega a la derecha
d.appendleft("izquierda") # O(1) — agrega a la izquierda
d.pop()                   # O(1) — quita de la derecha
d.popleft()               # O(1) — quita de la izquierda
```

### maxlen — descarte automático

```python
historial: deque[str] = deque(maxlen=3)

historial.append("Valencia")   # ['Valencia']
historial.append("Madrid")     # ['Valencia', 'Madrid']
historial.append("Barcelona")  # ['Valencia', 'Madrid', 'Barcelona']
historial.append("Sevilla")    # ['Madrid', 'Barcelona', 'Sevilla']
# Valencia fue descartada automáticamente
```

Con `maxlen`, la deque nunca crece más allá de N elementos. Cuando se llena,
el elemento más antiguo se descarta al agregar uno nuevo.

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_07/conceptos/03_deque_basico.py
```

---

## 4. deque vs list — cuándo usar cada uno

`list.pop(0)` desplaza todos los elementos un lugar para mantener la
contigüidad en memoria — es O(n). `deque.popleft()` actualiza un puntero — O(1).

```python
# Con lista — pop(0) es O(n)
lista = []
lista.append(item)
if len(lista) > MAXLEN:
    lista.pop(0)   # lento con listas grandes

# Con deque — automático O(1)
d = deque(maxlen=MAXLEN)
d.append(item)     # descarte automático si lleno
```

### Cuándo usar cada uno

| Necesitas | Usa |
|-----------|-----|
| Acceso por índice (`items[5]`) | `list` |
| Solo agregar/quitar del final | `list` |
| Agregar/quitar de ambos extremos | `deque` |
| Historial con tamaño fijo | `deque(maxlen=N)` |

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_07/conceptos/04_deque_vs_lista.py
```

---

## 5. dataclasses — tipos de datos sin boilerplate

`@dataclass` genera automáticamente `__init__`, `__repr__` y `__eq__`
a partir de las anotaciones de tipo del cuerpo de la clase.

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Consulta:
    timestamp: datetime
    city: str
    profiles: list[str] = field(default_factory=list)
```

Python genera `__init__(self, timestamp, city, profiles=<factory>)` de forma
automática.

### field() para defaults mutables

Los tipos mutables (listas, dicts) no pueden usarse como defaults directamente
en un `@dataclass` — se comparten entre instancias:

```python
# INCORRECTO — todas las instancias comparten la misma lista
@dataclass
class Mal:
    tags: list = []  # ValueError en Python 3.11+

# CORRECTO
@dataclass
class Bien:
    tags: list = field(default_factory=list)
```

### __str__ personalizado

```python
@dataclass
class Consulta:
    timestamp: datetime
    city: str

    def __str__(self) -> str:
        return f"[{self.timestamp:%H:%M}] {self.city}"
```

`@dataclass` genera `__repr__` automáticamente pero deja `__str__` a tu
criterio — es habitual definirlo para logs y salida al usuario.
