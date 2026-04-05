# Conceptos — Clase 07: Algoritmia Eficiente

`heapq` y `deque` son dos estructuras de la biblioteca estándar de Python
diseñadas para casos de uso específicos donde `list` no es la herramienta
correcta. Esta clase muestra cuándo y por qué usarlas.

---

## 1. heapq y deque — la estructura correcta para cada problema

La elección de estructura de datos no es un detalle de implementación:
define si el código es viable a escala o no.

### heapq — acceso al mínimo en O(1), inserción en O(log n)

`heapq` implementa un **min-heap** sobre una lista normal de Python.
El invariante del heap garantiza que `heap[0]` siempre es el elemento mínimo,
sin necesidad de ordenar toda la lista.

```python
import heapq

heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)

print(heap[0])              # 1 — el mínimo, en O(1)
print(heapq.heappop(heap))  # 1 — extrae el mínimo, en O(log n)
```

Para objetos, el patrón estándar es la tupla `(prioridad, item)`.
heapq compara el primer elemento y solo llega al segundo si hay empate:

```python
cola: list[tuple[int, str]] = []
heapq.heappush(cola, (3, "bajo"))
heapq.heappush(cola, (1, "urgente"))
heapq.heappush(cola, (2, "normal"))

prioridad, item = heapq.heappop(cola)
print(item)  # "urgente" — prioridad 1 sale primero
```

Para conjuntos de datos ya existentes, `nlargest` y `nsmallest` son
más expresivos que ordenar y cortar:

```python
tiempos_ruta = [8.5, 3.2, 12.1, 5.0, 9.7]

# Las 3 rutas más rápidas, sin modificar la lista original
print(heapq.nsmallest(3, tiempos_ruta))  # [3.2, 5.0, 8.5]
print(heapq.nlargest(2, tiempos_ruta))   # [12.1, 9.7]
```

### deque — O(1) en ambos extremos

`deque` (double-ended queue) es una lista doblemente enlazada.
A diferencia de `list`, permite insertar y quitar en cualquier extremo en O(1):

```python
from collections import deque

historial: deque[str] = deque(maxlen=3)
historial.append("Valencia")    # deque(['Valencia'])
historial.append("Madrid")      # deque(['Valencia', 'Madrid'])
historial.append("Barcelona")   # deque(['Valencia', 'Madrid', 'Barcelona'])
historial.append("Sevilla")     # deque(['Madrid', 'Barcelona', 'Sevilla'])
# Valencia descartada automáticamente — maxlen mantiene el invariante
```

### Cuándo usar cada estructura

| Necesitas | Usa | Por qué |
|-----------|-----|---------|
| Siempre el mínimo disponible, con inserciones | `heapq` | O(log n) push, O(1) peek |
| Ordenar todos los datos una sola vez | `sorted()` | O(n log n), más simple |
| Los N mejores/peores sin ordenar todo | `heapq.nlargest/nsmallest` | O(n log k) |
| Insertar/quitar al frente con frecuencia | `deque` | O(1) vs O(n) de `list` |
| Historial con tamaño máximo fijo | `deque(maxlen=N)` | Descarte automático |
| Acceso por índice | `list` | deque es O(n) por índice |

---

## 2. heapq — cola de prioridad con dataclass

### El problema de heapq con objetos complejos

`heapq` compara elementos con `<`. Si dos `ApiRequest` tienen la misma
prioridad, Python intenta comparar el siguiente campo. Si ese campo es
un `dict`, lanza `TypeError: '<' not supported`.

La solución: `@dataclass(order=True)` genera la comparación automáticamente,
y `field(compare=False)` excluye los campos que no son comparables.

```python
from dataclasses import dataclass, field

@dataclass(order=True)
class ApiRequest:
    prioridad: int                              # criterio principal
    timestamp: float = field(default_factory=time.time)  # desempate FIFO
    payload: dict = field(compare=False, default_factory=dict)  # excluido
```

Con `order=True`, heapq puede comparar instancias directamente sin tuplas.
El orden de los campos en el dataclass es el orden de comparación.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_07/conceptos/01_heapq_basico.py`

### Analiza la salida

```
Procesando peticiones por prioridad (Min-Heap):
[1] Procesando: maria_premium - write
[1] Procesando: ceo_admin - delete
[2] Procesando: juan_free - read
```

- `maria_premium` y `ceo_admin` tienen ambas prioridad 1, pero `maria_premium`
  llegó antes (menor `timestamp`). El campo `timestamp` actúa como desempate FIFO.
- `juan_free` con prioridad 2 sale al final, aunque fue insertado primero.
- `heappop` nunca devuelve datos en el orden de inserción — devuelve siempre
  el elemento con menor valor según la comparación del dataclass.

---

## 3. deque — ventana deslizante para rate limiting

### El patrón de ventana deslizante

Un rate limiter necesita responder en cada petición: "¿cuántas peticiones
se hicieron en los últimos N segundos?". El enfoque con `deque`:

```python
from collections import deque
import time

history: deque[float] = deque()  # sin maxlen — el tamaño lo controla el tiempo

def allow_request(history, max_req, window_secs) -> bool:
    now = time.time()
    # Descarta timestamps fuera de la ventana — popleft() es O(1)
    while history and history[0] <= now - window_secs:
        history.popleft()
    if len(history) < max_req:
        history.append(now)
        return True
    return False
```

La clave: `popleft()` elimina timestamps antiguos en O(1) porque deque
no necesita desplazar elementos. Con `list.pop(0)` sería O(n).

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_07/conceptos/02_deque_rate_limiter.py`

### Analiza la salida

```
Iniciando proteccion de Rate Limit (Max 3 req/2s)...
Peticion 1 -> [OK] ACEPTADA
Peticion 2 -> [OK] ACEPTADA
Peticion 3 -> [OK] ACEPTADA
Peticion 4 -> [BLOQUEADA] Too Many Requests
Peticion 5 -> [BLOQUEADA] Too Many Requests
[ESPERA] 2 segundos para que la ventana se limpie...
Peticion 6 -> [OK] ACEPTADA
```

- Las peticiones 1-3 llenan la ventana de 2 segundos.
- Las peticiones 4-5 llegan dentro de la misma ventana: bloqueadas.
- Tras 2 segundos, `allow_request()` llama a `popleft()` tres veces
  (elimina los 3 timestamps anteriores) y la petición 6 pasa.
- El historial del `deque` nunca supera 3 entradas durante la ráfaga.

---

## 4. deque con maxlen — ring buffer para streams de datos

### maxlen como invariante automático

Sin `maxlen`, gestionar un buffer de tamaño fijo requiere código manual:

```python
# Sin maxlen — gestión manual del tamaño
buffer = []
buffer.append(nuevo_evento)
if len(buffer) > MAX_SIZE:
    buffer.pop(0)   # O(n) — desplaza todos los elementos
```

Con `maxlen`, la estructura mantiene el invariante sola:

```python
# Con maxlen — gestión automática O(1)
buffer: deque[SystemEvent] = deque(maxlen=MAX_SIZE)
buffer.append(nuevo_evento)  # si lleno, descarta el más antiguo automáticamente
```

El descarte es silencioso e inmediato. No hay excepción, no hay lógica extra.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_07/conceptos/03_deque_basico.py`

### Analiza la salida

```
Ingiriendo Evento 1...
Estado del Buffer (Ocupacion: 1/3):  -> Evento 1: {'cpu': 41}
...
Ingiriendo Evento 4...
Estado del Buffer (Ocupacion: 3/3):  -> Evento 2  -> Evento 3  -> Evento 4
...
Ingiriendo Evento 5...
Estado del Buffer (Ocupacion: 3/3):  -> Evento 3  -> Evento 4  -> Evento 5
```

- Los eventos 1 y 2 desaparecen en cuanto llegan 4 y 5 respectivamente.
- La ocupación nunca supera 3/3 — el invariante se mantiene sin código adicional.
- `show_snapshot()` usa `self._buffer.maxlen` directamente: la deque
  expone su `maxlen` como atributo de solo lectura.
- En PyCommute, este patrón es el de `history.py`: retener las últimas N
  consultas sin acumular memoria ilimitada.

---

## 5. deque vs list — la diferencia de complejidad hecha visible

### Por qué list.insert(0) es lento

Una `list` en Python es un array contiguo en memoria. Insertar al frente
requiere desplazar todos los elementos una posición para hacer hueco:

```
Antes: [A, B, C, D]
insert(0, X)
Después: [X, A, B, C, D]   ← A, B, C, D se movieron todos
```

Con 250,000 elementos, cada inserción desplaza un promedio de 125,000
elementos. El tiempo total crece como O(n²).

`deque.appendleft()` actualiza un puntero — coste constante O(1),
independientemente del tamaño de la colección.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_07/conceptos/04_deque_vs_lista.py`

### Analiza la salida

```
[LISTA] Tiempo: ~12s
[DEQUE] Tiempo: ~0.01s
[RESULTADO] Deque fue ~1000 veces mas rapido.
```

- El tiempo de `list` escala cuadráticamente: cada nueva inserción es
  más lenta que la anterior porque hay más elementos que desplazar.
- El tiempo de `deque` escala linealmente: cada inserción cuesta lo mismo.
- La diferencia no importa con 10 elementos. Con 250,000 ya es x1000.
  Con 1,000,000 sería x16,000.
- La regla: si el algoritmo inserta o extrae del frente de forma habitual,
  `deque` no es una optimización — es la estructura correcta.
