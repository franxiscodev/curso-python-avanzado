# Conceptos — Clase 06: Eficiencia y Profiling

Tres técnicas para escribir código Python que no se arrastra cuando
la carga escala: medir con cProfile, procesar en streaming con generadores
y evitar cómputo repetido con lru_cache.

---

## 1. El ciclo de optimización — medir antes de tocar nada

La intuición sobre qué parte del código es lenta falla más de lo que acierta.
El ciclo correcto es:

```
1. Medir → cProfile da el mapa completo de todas las funciones
2. Identificar → buscar la función con alto tottime (tiempo propio)
3. Mejorar → aplicar la técnica adecuada
4. Volver a medir → confirmar que el cambio tuvo efecto
```

### Las tres herramientas de esta clase

| Herramienta | Cuándo usarla | Lo que resuelve |
|-------------|--------------|-----------------|
| `cProfile` | No sabes dónde está el problema | Da el mapa completo de todas las funciones |
| `generadores` | Tienes datos en páginas o streams | Evita cargar todo en memoria |
| `lru_cache` | La misma función se llama con los mismos args | Evita repetir el cómputo |

### Medir el tiempo de una función concreta: `time.perf_counter`

Cuando ya sabes qué función es el cuello de botella y quieres medir exactamente
cuánto tarda sin el overhead del profiler:

```python
import time

inicio = time.perf_counter()
resultado = fetch_clima("Valencia")
duracion = time.perf_counter() - inicio

print(f"fetch_clima tardó {duracion:.4f}s")
```

`perf_counter` es el reloj de mayor resolución disponible en Python.
Se usa para microbenchmarks de una función específica ya identificada.
Para comparar múltiples llamadas del mismo tipo, `timeit` (sección 5) es más preciso.

---

## 2. cProfile — el mapa completo del programa

### Qué registra

`cProfile` instrumenta cada llamada a función y registra:

| Columna | Qué mide |
|---------|----------|
| `ncalls` | Número de veces que se llamó a la función |
| `tottime` | Tiempo dentro de la función sin contar sus subcalls |
| `cumtime` | Tiempo total: función + todas las funciones que llama |

**Estrategia:** ordenar por `tottime` identifica la función que más CPU consume
por sí sola. Es el cuello de botella real.

### Patrón de uso

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
procesar_usuarios_legacy(payload_masivo)
profiler.disable()

stats = pstats.Stats(profiler).sort_stats('tottime')
stats.print_stats(5)  # top 5 funciones más costosas
```

El resultado es una tabla con las funciones que más tiempo consumen.
Sin este mapa, cualquier optimización es un disparo a ciegas.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_06/conceptos/01_cprofile_basico.py`

### Analiza la salida

El script valida 50,000 usuarios con Pydantic + `EmailStr`. La salida muestra
algo como:

```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
 50000    1.335    0.000   11.141    0.000  email_validator/syntax.py(validate_email_domain_name)
200000    1.075    0.000    4.043    0.000  idna/core.py(check_label)
```

- La función más costosa no es `procesar_usuarios_legacy` — es la validación
  del dominio del email dentro de `email-validator`.
- `ncalls=50000` confirma que se llama una vez por usuario.
- La conclusión: si el email no necesita validación IDNA completa, hay margen
  de optimización. Si la necesita, el cuello de botella es inherente al dominio.

---

## 3. Generadores con yield — procesamiento lazy

### El problema de cargar todo en memoria

```python
def fetch_todas_las_rutas() -> list[str]:
    all_routes = []
    for page in range(50):          # 50 páginas de API
        all_routes.extend(api_page(page))   # 10,000 rutas por página
    return all_routes               # retorna cuando tiene LAS 500,000
```

500,000 strings en una lista ocupan varios MB de RAM.
Si la API tiene 500 páginas en lugar de 50, ocupa 10x más.

### La solución: yield

```python
def fetch_rutas_paginadas():
    for page in range(50):
        pagina = api_page(page)
        for ruta in pagina:
            yield ruta   # devuelve una ruta, pausa, guarda el estado
```

`yield` hace dos cosas en cada iteración:
1. Entrega el valor al consumidor.
2. Pausa la función y guarda su estado completo (variables locales, posición).

El consumidor recibe la primera ruta antes de que se pidan las páginas
siguientes. El objeto generador solo ocupa ~200 bytes en memoria sin importar
cuántas rutas tenga.

### yield from — delegar en un generador interno

```python
def fetch_rutas_con_alternativas(perfil: str):
    yield from fetch_rutas_principales(perfil)   # delega al primer generador
    yield from fetch_rutas_alternativas(perfil)  # luego al segundo
```

`yield from` itera sobre el generador interno y re-emite cada valor
al consumidor externo. Equivale a un bucle `for item in gen: yield item`
pero más legible y eficiente.

### Cuándo NO usar generadores

- Necesitas `len()` o acceso por índice: `rutas[5]` no funciona.
- El mismo generador se itera más de una vez (se agota).
- El resultado debe pasarse a una función que requiere lista: `sorted()`, `json.dumps()`.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_06/conceptos/02_generadores_yield.py`

### Analiza la salida

```
RAM usada por Lista: 4.21 MB
RAM usada por Generador: 216 bytes (¡Casi cero!)
Primer valor procesado: Ruta_Geo_Data_0
```

- La lista materializa las 500,000 strings antes de retornar: 4+ MB.
- El generador es un objeto de estado de ~200 bytes; los datos se calculan
  bajo demanda.
- `next(rutas_generador)` consume solo el primer elemento. Las 499,999
  restantes no se calculan aún.
- En PyCommute, esto es crítico cuando la API de rutas devuelve cientos
  de páginas y el usuario solo necesita las primeras N.

---

## 4. lru_cache — no llamar a la API dos veces por lo mismo

### El problema

```python
# Sin cache: cada llamada hace una petición HTTP
clima_madrid = fetch_clima("Madrid")   # 800ms
clima_madrid = fetch_clima("Madrid")   # 800ms de nuevo — innecesario
```

Si 100 usuarios piden el clima de Madrid en el mismo minuto, se hacen
100 peticiones HTTP idénticas.

### La solución: @lru_cache

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fetch_clima(ciudad: str) -> str:
    return llamada_http(ciudad)   # solo se ejecuta la primera vez por ciudad

fetch_clima("Madrid")   # cache miss — ejecuta llamada_http
fetch_clima("Madrid")   # cache hit — retorna resultado guardado, 0ms
```

`lru_cache` guarda el resultado por cada combinación única de argumentos.
Cuando `maxsize=128` se llena, descarta la entrada menos usada recientemente
(Least Recently Used).

### Inspeccionar el estado del cache

```python
info = fetch_clima.cache_info()
# CacheInfo(hits=98, misses=2, maxsize=128, currsize=2)
```

- `misses=2`: solo se hicieron 2 llamadas reales (Madrid y Valencia).
- `hits=98`: los 98 usuarios restantes recibieron respuesta del cache.
- `cache_clear()`: vacía el cache, imprescindible para aislar tests.

### Limitación: argumentos hashables

`lru_cache` usa los argumentos como clave de dict interno.
Solo funciona con tipos hashables: `str`, `int`, `tuple`.
Pasar una lista lanza `TypeError`.

```python
# Solución para argumentos mutables:
def fetch_rutas_para_perfil(ciudades: list[str]) -> list[str]:
    return _fetch_rutas_cached(tuple(ciudades))   # convierte a tupla

@lru_cache
def _fetch_rutas_cached(ciudades: tuple[str, ...]) -> list[str]:
    ...
```

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_06/conceptos/03_lru_cache.py`

### Analiza la salida

```
--- Flujo de Usuarios en PyCommute ---
[HTTP] Consultando API para Madrid...
Usuario 1 pide: Clima actual en Madrid: Soleado, 24 grados
Tiempo: 1.5004s

[HTTP] Consultando API para Valencia...
Usuario 2 pide: Clima actual en Valencia: Soleado, 24 grados
Tiempo: 1.5004s

Usuario 3 pide: Clima actual en Madrid: Soleado, 24 grados
Tiempo: 0.0000s (CACHE HIT)

Metricas del Sistema de Cache:
CacheInfo(hits=1, misses=2, maxsize=128, currsize=2)
```

- Las dos primeras llamadas (Madrid, Valencia) tardan 1.5s cada una: son misses.
- La tercera (Madrid de nuevo) tarda 0s: es un hit. No hay llamada HTTP.
- `cache_info()` confirma: 2 misses, 1 hit. Solo 2 llamadas reales a la API.

---

## 5. Benchmark comparativo con timeit

### timeit vs time.perf_counter

`time.perf_counter` mide una ejecución. Es suficiente para funciones lentas
(I/O, sleep). Para funciones rápidas, una sola ejecución tiene demasiado ruido
(GC, interrupciones del OS).

`timeit` repite la función N veces y mide el total:

```python
import timeit

t = timeit.timeit(fetch_clima_cached, number=100_000)
print(f"100,000 llamadas en {t:.4f}s")
```

Al repetir muchas veces, el ruido por ejecución se vuelve insignificante.
El resultado es comparable y reproducible entre máquinas.

### El benchmark del script

`04_benchmark_comparativo.py` compara dos formas de procesar un `LocationDTO`:

```python
def parseo_manual():
    lat = float(raw_data["lat"])
    lon = float(raw_data["lon"])
    city = str(raw_data["city"])

def parseo_pydantic():
    return LocationDTO(**raw_data)
```

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_06/conceptos/04_benchmark_comparativo.py`

### Analiza la salida

```
Iniciando Benchmark: 500000 validaciones...
--------------------------------------------------
Parseo Manual (Python Puro): 0.08 segundos
Parseo Pydantic V2 (Rust):   0.46 segundos
```

- El parseo manual es más rápido para datos ya correctamente tipados:
  `float(39.4699)` es trivial en Python.
- Pydantic tiene overhead de instanciación del modelo aunque el core sea Rust.
- Esto no es un argumento contra Pydantic: su valor está en la **validación
  automática** (detecta `"abc"` donde se espera `float`), en los mensajes de
  error precisos y en la coerción desde strings (variables de entorno, JSON).
- `timeit` es la herramienta correcta aquí: 500,000 repeticiones eliminan el
  ruido y hacen la comparación significativa.
