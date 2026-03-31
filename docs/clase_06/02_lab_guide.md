# Clase 06 — Lab: Cache, Generadores y Profiling en PyCommute

---

## ¿Por qué construimos esto así?

En Clase 5 PyCommute hace llamadas async a dos APIs en paralelo. Funciona bien,
pero cada vez que necesitamos las coordenadas de Valencia las buscamos de nuevo
desde cero. Si el usuario consulta la misma ciudad diez veces en una sesión,
hacemos diez búsquedas idénticas.

Esta clase introduce tres técnicas complementarias:

**`lru_cache`** en un módulo `cache.py` separado: las coordenadas de una ciudad
son siempre las mismas — es el caso perfecto para memoización. Separamos el cache
de la orquestación porque son responsabilidades distintas. Si mañana cambiamos
de coordenadas hardcodeadas a una API real, solo tocamos `cache.py`.

**`AsyncGenerator`** en `iter_routes()`: en vez de construir una lista completa
de rutas en memoria antes de procesarlas, las generamos una por una. El beneficio
se hace evidente con muchos perfiles de ruta, y en Clase 12 (FastAPI) este mismo
patrón permite hacer streaming de respuestas.

**`cProfile`** como wrapper opcional: el código de producción no se toca. La
función `get_commute_info_profiled()` envuelve la función principal sin modificarla,
y el profiling se activa solo cuando se necesita. El principio: medir primero,
optimizar después.

---

## Paso 1 — Perfilar el demo de Clase 5

Antes de optimizar, medimos. Ejecuta el demo de Clase 5 bajo cProfile para
ver el estado actual.

```python
import cProfile, pstats, io
# envuelve la llamada con profiler.enable() / profiler.disable()
```

Aplicamos la sección de cProfile de `01_conceptos.md`.

¿Qué función domina `cumtime`? ¿Era lo esperado?

---

## Paso 2 — Crear `cache.py`

Crea `curso/src/pycommute/cache.py` con el registro de coordenadas y
la función memoizada.

```python
from functools import lru_cache
from loguru import logger

_COORDENADAS: dict[str, tuple[float, float]] = {
    "Valencia": (39.4699, -0.3763),
    "Madrid":   (40.4168, -3.7038),
    "Barcelona": (41.3851, 2.1734),
    "Sevilla":  (37.3891, -5.9845),
    "Bilbao":   (43.2630, -2.9350),
}

@lru_cache(maxsize=128)
def get_coordinates(city: str) -> tuple[float, float]:
    """..."""
    city_normalized = city.strip().title()
    if city_normalized not in _COORDENADAS:
        raise ValueError(f"Ciudad no encontrada: {city_normalized}")
    return _COORDENADAS[city_normalized]

def cache_info() -> str:
    """Devuelve estadísticas del cache."""
    info = get_coordinates.cache_info()
    return f"hits={info.hits}, misses={info.misses}, ..."
```

Ver sección 4 de `01_conceptos.md` para la sintaxis completa de `lru_cache`.

---

## Paso 3 — Modificar `commute.py`

Agrega `iter_routes()` como `AsyncGenerator` y `get_commute_info_profiled()`
como wrapper de profiling.

**`iter_routes()`:**
```python
from typing import AsyncGenerator

async def iter_routes(
    origin: tuple[float, float],
    destination: tuple[float, float],
    profiles: list[str],
    api_key: str,
) -> AsyncGenerator[dict[str, Any], None]:
    for profile in profiles:
        route = await get_route(origin, destination, profile, api_key)
        yield route
```

Ver sección 3 de `01_conceptos.md` para la sintaxis de `AsyncGenerator`.

**`get_commute_info_profiled()`:**
```python
import cProfile, pstats, io

async def get_commute_info_profiled(...) -> dict[str, Any]:
    profiler = cProfile.Profile()
    profiler.enable()
    result = await get_commute_info(...)
    profiler.disable()
    # ... pstats + logger.debug
    return result
```

`get_commute_info()` no se modifica — el profiling es una capa externa.

---

## Paso 4 — Crear `test_cache.py`

Crea `curso/tests/unit/test_cache.py` con tres tests:

```python
from pycommute.cache import get_coordinates

def test_get_coordinates_returns_correct_values() -> None:
    lat, lon = get_coordinates("Valencia")
    assert abs(lat - 39.4699) < 0.001
    assert abs(lon - (-0.3763)) < 0.001

def test_get_coordinates_uses_cache() -> None:
    get_coordinates.cache_clear()  # aislar el estado del cache
    get_coordinates("Madrid")
    get_coordinates("Madrid")
    info = get_coordinates.cache_info()
    assert info.hits >= 1
    assert info.misses == 1

def test_get_coordinates_raises_for_unknown_city() -> None:
    with pytest.raises(ValueError, match="Ciudad no encontrada"):
        get_coordinates("CiudadInventada")
```

El `cache_clear()` en el segundo test es crítico: sin él, llamadas de
otros tests acumulan hits y el assert `misses == 1` puede fallar.

---

## Paso 5 — Verificar

```bash
# Windows (PowerShell)
cd curso
uv run pytest tests/ -v

# Linux
cd curso
uv run pytest tests/ -v
```

Resultado esperado: 22 tests en verde.

---

## Paso 6 — Verificar el hito

```bash
# Windows (PowerShell) / Linux
uv run scripts/clase_06/demo_proyecto.py
```

Salida esperada:
```
INFO | Cache tras primera llamada: hits=0, misses=1, currsize=1
INFO | Cache tras segunda llamada: hits=1, misses=1, currsize=1
INFO | Procesando 3 rutas con generador...
INFO | Ruta 1: X.X km, XX min (cycling-regular)
...
```

El `hits=1` confirma que la segunda llamada a `get_coordinates("Valencia")`
se resolvió desde cache sin ejecutar la función.

---

## Snapshot de la clase

El estado final del código está en:

```
curso/snapshots/clase_06/
├── src/pycommute/
│   ├── cache.py        ← nuevo, con comentarios [CLASE 6]
│   └── commute.py      ← generador + profiling, con comentarios
└── tests/unit/
    └── test_cache.py
```

Usa este snapshot como referencia si algo no encaja durante el lab.
