# Clase 06 — Conceptos: Eficiencia y Profiling

---

## 1. cProfile — medir antes de optimizar

Antes de optimizar cualquier cosa, hay que medir. La intuición sobre qué
parte del código es lenta falla más de lo que acierta.

`cProfile` es el profiler estándar de Python. Registra cuánto tiempo se
gasta en cada función del programa.

### Uso básico

```python
import cProfile
import pstats
import io

profiler = cProfile.Profile()
profiler.enable()          # comienza a medir
resultado = mi_funcion()
profiler.disable()         # deja de medir

# Mostrar resultados ordenados por tiempo acumulado
stream = io.StringIO()
stats = pstats.Stats(profiler, stream=stream)
stats.sort_stats("cumulative")
stats.print_stats(10)      # top 10 funciones más lentas
print(stream.getvalue())
```

### Interpretar los resultados

```
ncalls  tottime  percall  cumtime  percall  filename:lineno(function)
     1    0.000    0.000    0.100    0.100  mi_script.py:10(programa)
     1    0.100    0.100    0.100    0.100  {built-in method time.sleep}
```

| Columna | Qué mide |
|---------|----------|
| `ncalls` | Número de veces que se llamó a la función |
| `tottime` | Tiempo dentro de la función (sin contar sus subcalls) |
| `cumtime` | Tiempo total: función + todas las funciones que llama |

**Estrategia:** ordenar por `cumtime` identifica el árbol más costoso.
Bajar por él hasta encontrar la función con alto `tottime` es el cuello
de botella real.

### Cuándo usarlo

- Tienes código lento pero no sabes dónde.
- Quieres confirmar que tu optimización tuvo efecto.
- Quieres comparar dos implementaciones.

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_06/conceptos/01_cprofile_basico.py
```

---

## 2. Generadores — procesamiento lazy

Un generador calcula valores bajo demanda, uno a la vez.
Esto ahorra memoria cuando no necesitas todos los resultados a la vez.

### yield — la clave del generador

```python
def cuadrados(n: int):
    for i in range(n):
        yield i * i  # pausa aquí, retorna el valor, guarda el estado
```

`yield` hace dos cosas:
1. Retorna el valor al consumidor.
2. Pausa la función y guarda su estado completo.

La próxima vez que el consumidor pida un valor, la función retoma
exactamente donde se quedó.

### Lista vs Generador

```python
# Lista — construye todo en memoria antes de retornar
valores = [i * i for i in range(1_000_000)]  # ocupa ~8 MB

# Generador — calcula uno por uno, bajo demanda
valores = (i * i for i in range(1_000_000))  # ocupa ~200 bytes
```

La diferencia importa cuando:
- El dataset no cabe en RAM.
- Solo necesitas procesar los primeros N elementos.
- Construyes un pipeline de transformaciones.

### Cuándo NO usar generadores

- Necesitas acceso por índice: `items[5]` no funciona con generadores.
- Necesitas `len()` antes de iterar.
- El mismo generador se va a iterar más de una vez (se agota).

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_06/conceptos/02_generadores_yield.py
```

---

## 3. AsyncGenerator — yield en funciones async

Un `AsyncGenerator` combina la laziness de los generadores con la
capacidad de hacer `await` entre valores.

```python
from typing import AsyncGenerator

async def gen_datos() -> AsyncGenerator[int, None]:
    for i in range(5):
        await hacer_algo_async()  # puede hacer await entre yields
        yield i
```

El consumidor usa `async for`:

```python
async def main():
    async for valor in gen_datos():
        print(valor)
```

### Diferencia con un generador síncrono

Un generador síncrono no puede hacer `await`. Si la función que genera
datos hace I/O (API calls, base de datos), necesitas un `AsyncGenerator`.

```python
# Esto NO funciona en un generador síncrono
def gen_rutas():
    for profile in profiles:
        route = await get_route(...)  # SyntaxError — no puede await aquí
        yield route

# Esto SÍ funciona en un AsyncGenerator
async def iter_rutas() -> AsyncGenerator[dict, None]:
    for profile in profiles:
        route = await get_route(...)  # await dentro de async def — ok
        yield route
```

---

## 4. lru_cache — cachear resultados costosos

`lru_cache` guarda el resultado de llamadas anteriores en memoria.
Si la misma función se llama con los mismos argumentos, retorna el
resultado guardado sin ejecutar la función de nuevo.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_coordinates(city: str) -> tuple[float, float]:
    # Esta función solo se ejecuta la primera vez por cada `city`
    return buscar_coordenadas(city)

get_coordinates("Valencia")  # ejecuta la función (cache miss)
get_coordinates("Valencia")  # retorna desde cache (cache hit, cero cómputo)
```

### Inspeccionar el cache

```python
info = get_coordinates.cache_info()
# CacheInfo(hits=5, misses=3, maxsize=128, currsize=3)
```

- `hits`: cuántas veces se evitó el cómputo.
- `misses`: cuántas veces se ejecutó la función real.
- `cache_clear()`: vacía el cache (útil en tests).

### Limitación importante

Solo funciona con argumentos **hashables**: `str`, `int`, `tuple`, etc.
No funciona con listas ni diccionarios.

```python
@lru_cache
def func(items: list[int]) -> int:  # TypeError al llamar — lista no es hashable
    ...
```

Solución: convertir la lista a tupla antes de llamar a la función cacheada.

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_06/conceptos/03_lru_cache.py
```

### Comparativa de las tres técnicas

```
uv run scripts/clase_06/conceptos/04_benchmark_comparativo.py
```
