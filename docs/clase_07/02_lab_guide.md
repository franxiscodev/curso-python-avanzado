# Clase 07 — Lab: Ranking e Historial en PyCommute

---

## ¿Por qué construimos esto así?

PyCommute ya obtiene rutas en paralelo. El siguiente paso natural es
**hacer algo útil con ellas**: ordenarlas por prioridad y recordar las
consultas pasadas.

**`ranking.py` con heapq**: `sorted()` también ordena rutas, y para 3
perfiles la diferencia es cero. La decisión pedagógica es correcta:
cuando el sistema crezca a consultas en tiempo real con muchos perfiles,
`heapq.heappush()` en O(log n) escala; reordenar toda la lista con
`sorted()` en cada inserción no. Usamos la herramienta diseñada para
el problema, no la más cómoda para el caso trivial.

**`history.py` con deque**: mantener las últimas N consultas con una lista
requiere `pop(0)` — O(n). `deque(maxlen=N)` hace lo mismo en O(1) y además
elimina el código de gestión del tamaño. El invariante lo garantiza la
estructura, no el programador.

**Dos módulos separados**: ranking y memoria son responsabilidades distintas.
Si mañana el criterio de ranking cambia (agregar penalización por lluvia),
solo tocamos `ranking.py`. Si el historial necesita persistencia en base de
datos, solo tocamos `history.py`. Esta separación no es accidental — prepara
directamente la Clase 8 donde cada módulo se convierte en un componente
del sistema hexagonal.

---

## Paso 1 — Explorar los scripts de conceptos

Antes de escribir código del proyecto, ejecuta los scripts para ver las
estructuras en acción:

```bash
# Windows (PowerShell) / Linux
uv run scripts/clase_07/conceptos/01_heapq_basico.py
uv run scripts/clase_07/conceptos/02_heapq_objetos.py
uv run scripts/clase_07/conceptos/03_deque_basico.py
uv run scripts/clase_07/conceptos/04_deque_vs_lista.py
```

Observar en `02_heapq_objetos.py` el patrón `(prioridad, índice, objeto)` —
es el mismo que usaremos en `ranking.py`.

---

## Paso 2 — Crear `ranking.py`

Crea `curso/src/pycommute/ranking.py` con tres funciones.

Aplicamos la sección 1 y 2 de `01_conceptos.md`.

```python
import heapq
from typing import Any
from loguru import logger

def rank_routes_by_time(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not routes:
        return []
    heap: list[tuple[float, int, dict[str, Any]]] = []
    for i, route in enumerate(routes):
        heapq.heappush(heap, (route["duration_min"], i, route))
    ranked = []
    while heap:
        _, _, route = heapq.heappop(heap)
        ranked.append(route)
    return ranked

def get_best_route(routes: list[dict[str, Any]], by: str = "time") -> dict[str, Any]:
    if not routes:
        raise ValueError("No hay rutas para rankear")
    key_map = {"time": "duration_min", "distance": "distance_km"}
    if by not in key_map:
        raise ValueError(f"Criterio inválido: {by}. Usar 'time' o 'distance'")
    key = key_map[by]
    return heapq.nsmallest(1, routes, key=lambda r: r[key])[0]
```

Ver la spec completa en el snapshot.

---

## Paso 3 — Crear `history.py`

Crea `curso/src/pycommute/history.py` con `ConsultaEntry` y `ConsultaHistory`.

Aplicamos las secciones 3, 4 y 5 de `01_conceptos.md`.

```python
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class ConsultaEntry:
    timestamp: datetime
    city: str
    profiles: list[str]
    weather: dict[str, Any]
    routes: list[dict[str, Any]]

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M")
        return f"[{ts}] {self.city} -> {', '.join(self.profiles)}"

class ConsultaHistory:
    def __init__(self, maxlen: int = 10) -> None:
        self._history: deque[ConsultaEntry] = deque(maxlen=maxlen)

    def add(self, city: str, profiles: list[str],
            weather: dict, routes: list[dict]) -> None:
        self._history.append(ConsultaEntry(
            timestamp=datetime.now(), city=city,
            profiles=profiles, weather=weather, routes=routes,
        ))

    def get_recent(self, n: int | None = None) -> list[ConsultaEntry]:
        entries = list(self._history)
        entries.reverse()
        return entries[:n] if n else entries
```

---

## Paso 4 — Crear `test_ranking.py`

Crea `curso/tests/unit/test_ranking.py` con al menos 4 tests:

```python
ROUTES = [
    {"profile": "foot-walking",    "distance_km": 1.8, "duration_min": 22},
    {"profile": "driving-car",     "distance_km": 2.1, "duration_min": 5},
    {"profile": "cycling-regular", "distance_km": 2.0, "duration_min": 8},
]

def test_rank_routes_by_time_orders_ascending():
    ranked = rank_routes_by_time(ROUTES)
    assert ranked[0]["profile"] == "driving-car"  # la más rápida
    assert ranked[0]["duration_min"] <= ranked[1]["duration_min"]

def test_get_best_route_by_time_returns_fastest():
    best = get_best_route(ROUTES, by="time")
    assert best["profile"] == "driving-car"
```

---

## Paso 5 — Crear `test_history.py`

Crea `curso/tests/unit/test_history.py` con 3 tests:

```python
def test_history_respects_maxlen():
    history = ConsultaHistory(maxlen=3)
    for city in ["Valencia", "Madrid", "Barcelona", "Sevilla"]:
        history.add(city, ["cycling-regular"], WEATHER, ROUTES)
    assert len(history) == 3
    assert "Valencia" not in [e.city for e in history.get_recent()]
```

El `maxlen=3` con 4 inserciones verifica el descarte automático.

---

## Paso 6 — Verificar

```bash
# Windows (PowerShell) / Linux
cd curso
uv run pytest tests/ -v
```

Resultado esperado: 31 tests en verde.

---

## Paso 7 — Verificar el hito

```bash
# Windows (PowerShell) / Linux
uv run scripts/clase_07/demo_proyecto.py
```

Salida esperada:
```
INFO | Rutas rankeadas por tiempo (mejor primero):
INFO |   1. driving-car: ... km, ... min
INFO |   2. cycling-regular: ... km, ... min
INFO |   3. foot-walking: ... km, ... min
INFO | Historial (4 consultas):
INFO |   [YYYY-MM-DD HH:MM] Sevilla -> cycling-regular, ...
```

---

## Snapshot de la clase

El estado final del código está en:

```
curso/snapshots/clase_07/
├── src/pycommute/
│   ├── ranking.py    ← nuevo, con comentarios [CLASE 7]
│   └── history.py    ← nuevo, con comentarios [CLASE 7]
└── tests/unit/
    ├── test_ranking.py
    └── test_history.py
```

Los comentarios `[CLASE 8 →]` en el snapshot anticipan la reorganización
hexagonal de la semana siguiente.
