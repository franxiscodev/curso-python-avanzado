# Clase 05 — Concurrencia Estructurada con async/await y anyio

---

## 1. Concurrencia vs Paralelismo

**Concurrencia** es sobre estructura: un programa está diseñado para manejar
múltiples tareas que progresan de forma intercalada. Una tarea se pausa mientras
espera algo (una respuesta de red, un archivo), y otra avanza en ese hueco.

**Paralelismo** es sobre ejecución simultánea: múltiples tareas corren literalmente
al mismo tiempo en distintos núcleos del procesador.

Un cocinero que pone agua a hervir, corta verduras mientras espera, y vuelve a la
olla cuando hierve, es **concurrente**. Dos cocineros en cocinas separadas son
**paralelos**.

### El GIL de Python: por qué async funciona para I/O

Python tiene el **GIL** (Global Interpreter Lock): solo un hilo puede ejecutar
bytecode Python a la vez. Esto elimina el paralelismo real para código CPU-bound.

Sin embargo, el GIL se **libera automáticamente** durante operaciones de I/O
(esperar una respuesta de red, leer disco). Mientras el kernel espera que llegue
el paquete HTTP, Python puede hacer otra cosa.

`async/await` hace esto explícito: en cada `await`, el hilo cede el control al
event loop, que puede ejecutar otras coroutines mientras la I/O está pendiente.

### Cuándo usar cada herramienta

| Caso de uso | Herramienta |
|---|---|
| Múltiples peticiones HTTP concurrentes | `async/await` |
| I/O de red o disco con esperas | `async/await` |
| Cálculos intensivos (CPU-bound) | `multiprocessing` |
| Librerías síncronas de terceros en paralelo | `threading` |
| Código ya async (FastAPI, etc.) | `async/await` nativo |

La regla: si tu código pasa más tiempo **esperando** que **calculando**, async
es la herramienta correcta.

En la sección siguiente verás async/await en acción.

---

## 2. async/await en Python

### Qué es una coroutine

`async def` define una **coroutine function**. Llamarla no ejecuta nada: devuelve
un objeto coroutine que el event loop puede planificar.

```python
async def fetch_clima(ciudad: str) -> dict:
    await anyio.sleep(0.3)   # simula I/O — cede el control aquí
    return {"ciudad": ciudad, "temp": 18}

# Esto NO ejecuta fetch_clima:
coro = fetch_clima("Valencia")   # <coroutine object fetch_clima at 0x...>
```

Para ejecutarla, necesitas `await` dentro de otra coroutine, o `anyio.run()` como
punto de entrada:

```python
import anyio

async def main() -> None:
    datos = await fetch_clima("Valencia")   # ahora sí ejecuta
    print(datos)

anyio.run(main)   # lanza el event loop y bloquea hasta que main() termina
```

### Qué hace await

`await` hace dos cosas:

1. Inicia la ejecución de la coroutine indicada.
2. Suspende la coroutine actual hasta que la otra termina, **devolviendo el control
   al event loop** para que pueda ejecutar otras tareas mientras espera.

### Error común: olvidar await

Si llamas a una coroutine sin `await`, Python no ejecuta nada y emite
`RuntimeWarning: coroutine was never awaited`:

```python
async def main() -> None:
    datos = fetch_clima("Valencia")   # MAL: datos es <coroutine object>
    print(datos["temp"])              # KeyError — no es un dict

    datos = await fetch_clima("Valencia")   # BIEN: datos es {"ciudad": ..., "temp": 18}
```

Regla: si la función es `async def`, siempre se llama con `await`.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_05/conceptos/01_async_await_basico.py

---

### Análisis de 01_async_await_basico.py

El script tiene dos coroutines y un `main()` que las llama en secuencia.

**Por qué los delays son distintos (0.1s y 2.0s):**
`fetch_cache` simula una consulta a Redis — muy rápida, casi local.
`fetch_api_externa` simula una llamada a una API de terceros — lenta por red.
La diferencia hace visible la asimetría real que existe en cualquier sistema.

**Qué significa "secuencial intencional":**
El comentario en `main()` dice que las dos llamadas son secuenciales adrede.
`await fetch_cache(...)` bloquea `main()` hasta que termina; solo entonces
empieza `await fetch_api_externa(...)`. El event loop *podría* ejecutar otras
coroutines durante esos awaits, pero aquí no hay otras: están solas.

**Por qué el tiempo total es ~2.1s:**
Es la suma de ambos delays: 0.1s + 2.0s = 2.1s. Esto es lo característico de
la ejecución secuencial. Si las dos coroutines corrieran en paralelo, el tiempo
sería el máximo de los dos: ~2.0s.

**Qué cambia en la sección 3:**
`create_task_group()` permite lanzar ambas coroutines al mismo tiempo. En ese
caso, el tiempo total pasa de la suma al máximo — esa es la ganancia de la
concurrencia.

---

## 3. anyio — Concurrencia Estructurada

### Por qué anyio

Python tiene `asyncio` en la librería estándar. `anyio` es una capa sobre
`asyncio` (y `trio`) que ofrece:

- **API más ergonómica**: `create_task_group()` es más claro que `asyncio.gather()`.
- **Backend-agnostic**: el mismo código funciona sobre `asyncio` o `trio`.
- **Compatible con FastAPI**: FastAPI usa `anyio` internamente.

### create_task_group() — tareas que no se escapan

La concurrencia estructurada garantiza que las tareas hijas no sobreviven al bloque
que las creó. Cuando sale del `async with`, todas han terminado o fallado:

```python
import anyio

async def main() -> None:
    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch_clima, "Valencia")
        tg.start_soon(fetch_ruta, "Alicante", "Madrid")
    # aquí ambas tareas han terminado — el tiempo es el máximo, no la suma
```

### Patrón del dict compartido para recoger resultados

`start_soon()` no retorna el valor de la tarea. Para recoger resultados, se pasa
un diccionario compartido que cada tarea rellena:

```python
async def main() -> None:
    resultados: dict[str, Any] = {}

    async with anyio.create_task_group() as tg:
        tg.start_soon(_fetch_clima, "Valencia", resultados)
        tg.start_soon(_fetch_ruta, "Alicante", "Madrid", resultados)

    # el dict está completo aquí
    clima = resultados["clima"]
    ruta = resultados["ruta"]
```

### ExceptionGroup y except*

Si una tarea lanza una excepción, el task group cancela las demás y agrupa los
errores en un `ExceptionGroup`. Para capturarlo se usa `except*` (Python 3.11+):

```python
try:
    async with anyio.create_task_group() as tg:
        tg.start_soon(tarea_a)
        tg.start_soon(tarea_b)
except* RuntimeError as eg:
    for exc in eg.exceptions:
        print(f"Falló: {exc}")
```

`except*` es distinto de `except`: puede capturar grupos de excepciones y sigue
ejecutando el resto del `for` aunque haya varias.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_05/conceptos/02_anyio_task_group.py

---

### Análisis de 02_anyio_task_group.py

El script lanza tres servicios en paralelo con latencias distintas y demuestra
qué ocurre cuando uno falla.

**Por qué los tres servicios tienen latencias distintas (2.0s, 1.5s, 0.5s):**
Se elige que `Ollama_Fallback` sea el más rápido (0.5s) para que su fallo
ocurra mientras los otros dos siguen trabajando. Si todos fallaran al mismo
tiempo no se vería la cancelación en cascada.

**Por qué OpenWeather y OpenRoute se cancelan:**
Cuando `Ollama_Fallback` lanza `RuntimeError` a los 0.5s, `create_task_group()`
cancela inmediatamente todas las tareas que siguen activas. OpenRoute llevaba
0.5s de sus 1.5s; OpenWeather llevaba 0.5s de sus 2.0s. Ambas reciben la señal
de cancelación y se interrumpen.

**Qué hace `except anyio.get_cancelled_exc_class()` y por qué es CRÍTICO relanzar:**
Cada tarea tiene un `try/except` que captura la excepción de cancelación para
poder loguear un mensaje. Pero después del `logger.warning(...)` hay un `raise`
obligatorio. Si no se relanza, anyio interpreta que la tarea terminó limpiamente:
el task group no sabe que fue cancelada, y el mecanismo de structured concurrency
se rompe. El `raise` le dice a anyio "sigo siendo una cancelación, propaga esto".

**Qué pasaría si se quitara el `raise`:**
`fetch_service` terminaría sin error aunque hubiera sido cancelada. El task group
esperaría a que todas las tareas terminaran "correctamente", y el `RuntimeError`
de `Ollama_Fallback` podría perderse o comportarse de forma impredecible.

**Por qué `except* RuntimeError` en lugar de `except RuntimeError`:**
anyio envuelve las excepciones en un `ExceptionGroup`. `except RuntimeError` no
captura un `ExceptionGroup` que contiene `RuntimeError`; `except*` sí. El `for`
sobre `eg.exceptions` itera cada excepción individualmente.

---

## 4. httpx.AsyncClient — Cliente HTTP Asíncrono

### httpx.Client vs httpx.AsyncClient

`httpx` ofrece dos interfaces con la misma API:

```python
# Síncrono — bloquea el hilo hasta recibir respuesta
with httpx.Client() as client:
    respuesta = client.get("https://api.openweathermap.org/...")

# Asíncrono — cede el event loop mientras espera
async with httpx.AsyncClient() as client:
    respuesta = await client.get("https://api.openweathermap.org/...")
```

La diferencia es `async with` y `await`. La interfaz, los parámetros y el manejo
de errores son idénticos.

### async with — cierre garantizado

`httpx.AsyncClient` es un context manager asíncrono. `async with` garantiza que
la conexión se cierra correctamente al salir del bloque, incluso si ocurre una
excepción. Es el equivalente async de `with httpx.Client()`.

### Connection pooling y Keep-Alive

`AsyncClient` mantiene un pool de conexiones TCP abiertas y las reutiliza. Si
creas un cliente nuevo por cada request, cada llamada paga el coste de establecer
la conexión (y el TLS handshake si es HTTPS: ~150ms extra). Con un cliente
compartido, solo se paga una vez.

La regla: **un solo cliente para toda la vida de la función**. No crear uno por
cada coroutine.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_05/conceptos/03_httpx_async_client.py

---

### Análisis de 03_httpx_async_client.py

El script descarga 5 posts de una API pública en paralelo, valida cada respuesta
con Pydantic y muestra el resultado.

**Por qué un único cliente compartido entre las 5 tareas:**
El cliente se crea en `main()` antes del task group y se pasa a cada llamada de
`fetch_post`. Así las 5 coroutines comparten el mismo pool de conexiones. Si cada
`fetch_post` creara su propio `AsyncClient`, habría 5 handshakes TLS en lugar de
uno. El comentario en el código lo explica explícitamente.

**Qué hace `Post.model_validate(response.json())`:**
`response.json()` devuelve un `dict` en crudo. `model_validate()` lo parsea y
valida contra el modelo `Post`: comprueba que existan los campos `id` (int) y
`title` (str) con los tipos correctos. Si la API devuelve algo inesperado, lanza
`ValidationError` en lugar de un `KeyError` misterioso varias líneas después.
Es el mismo patrón de contratos que usamos en `src/pycommute`.

**Qué pasa si no hay internet:**
Cada `fetch_post` tiene un `except httpx.HTTPError` que captura cualquier error
de red y logua un mensaje de error sin propagar la excepción. El task group
continúa con las tareas restantes. El script termina sin traceback.

**Por qué los posts llegan en orden distinto cada vez:**
Las 5 coroutines se lanzan casi al mismo tiempo y cada una espera la respuesta
de la red. La que recibe respuesta primero logua primero. El orden depende de
la latencia de cada request en cada ejecución — no hay nada determinista.

---

## 5. Benchmark: Síncrono vs Asíncrono

### Por qué async es más rápido para I/O bound

En modo síncrono, cada petición HTTP espera a que la anterior termine. El tiempo
total es la suma de todas las esperas:

```
Síncrono:   |----req1----|----req2----|----req3----|----req4----|----req5----|
            0s                                                              5s
```

En modo async con task group, todas las peticiones se lanzan a la vez. Cada una
espera su respuesta de forma independiente. El tiempo total es el máximo, no la
suma:

```
Asíncrono:  |----req1----|
            |----req2----|
            |----req3----|
            |----req4----|
            |----req5----|
            0s           ~1s
```

Con 5 requests de 1s cada una: síncrono tarda ~5s, asíncrono tarda ~1s. La
ganancia escala con el número de requests independientes.

---

▶ Ejecuta el ejemplo (tarda ~6s en total — es intencional):
  uv run python scripts/clase_05/conceptos/04_sync_vs_async_benchmark.py

---

### Análisis de 04_sync_vs_async_benchmark.py

El script hace 5 peticiones reales a `httpbin.org/delay/1` — un endpoint que
tarda exactamente 1 segundo en responder — primero en modo síncrono y luego en
modo asíncrono.

**Por qué `logger.error()` para el tiempo síncrono:**
`logger.error()` muestra el mensaje en rojo en la mayoría de terminales. No es
un error real: es una elección visual deliberada para que el tiempo síncrono
destaque como "malo" frente al tiempo asíncrono. `logger.warning()` para el
inicio síncrono y `logger.success()` para el asíncrono refuerzan el mismo
contraste visual.

**Por qué `logger.success()` para el asíncrono:**
El verde de `success` comunica "esto es lo correcto" sin necesidad de texto
adicional. El output del script es una demostración visual, no solo numérica.

**Qué significa `PETICIONES = 5` y qué pasaría con 10:**
Con `PETICIONES = 5` el síncrono tarda ~5s y el asíncrono ~1s. Si se cambia a
`PETICIONES = 10`, el síncrono tardaría ~10s y el asíncrono seguiría tardando
~1s: la ganancia en absoluto crece linealmente, pero el asíncrono no empeora
porque las 10 peticiones corren en paralelo.

**Por qué se elimina el handler de loguru al inicio:**
Las dos líneas al final del script hacen esto:

```python
logger.remove()
logger.add(sys.stderr, format="<level>{message}</level>")
```

El handler por defecto de loguru incluye timestamp, módulo y nivel en cada línea.
Para esta demo, ese formato ensancha el output y distrae del tiempo. El nuevo
handler solo muestra el mensaje con el color de nivel — más limpio para una
comparación visual.

---

## 6. Tests Async con @pytest.mark.anyio

### Por qué un test síncrono no funciona con funciones async

Llamar a una coroutine sin `await` devuelve el objeto coroutine, no el resultado.
Un test síncrono que haga esto nunca compara el valor real:

```python
# MAL — test síncrono intentando testar una función async
def test_fetch_clima():
    resultado = fetch_clima("Valencia")   # <coroutine object> — no ejecuta nada
    assert resultado["temp"] == 18        # TypeError: 'coroutine' is not subscriptable
```

Para ejecutar la coroutine en un test se necesita un event loop. `pytest-anyio`
lo gestiona automáticamente cuando el test es `async def` y lleva el marker
`@pytest.mark.anyio`.

### @pytest.mark.anyio

```python
import pytest

@pytest.mark.anyio
async def test_fetch_clima():
    resultado = await fetch_clima("Valencia")
    assert resultado["temp"] == 18
```

pytest-anyio crea un event loop limpio para el test, ejecuta la coroutine, y lo
cierra al terminar. Cada test tiene su propio loop — no hay estado compartido
entre tests.

### AsyncMock — mockear una coroutine

`AsyncMock` es el equivalente async de `MagicMock`. Cuando se `await`-ea, devuelve
`return_value`. Permite aislar una función en el test sin ejecutar su lógica real:

```python
from unittest.mock import AsyncMock

@pytest.mark.anyio
async def test_commute_llama_ambas_apis(monkeypatch):
    mock_clima = AsyncMock(return_value={"temp": 18})
    mock_ruta = AsyncMock(return_value={"duracion": 45})
    monkeypatch.setattr("pycommute.services.commute.fetch_clima", mock_clima)
    monkeypatch.setattr("pycommute.services.commute.fetch_ruta", mock_ruta)

    resultado = await get_commute_info("Valencia", "A", "B")

    mock_clima.assert_awaited_once()
    mock_ruta.assert_awaited_once()
```

`assert_awaited_once_with()` verifica que la coroutine fue llamada con `await`
y con los argumentos exactos. `assert_called_once_with()` (el equivalente síncrono)
no verificaría el `await`.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_05/conceptos/05_tests_async.py

---

### Análisis de 05_tests_async.py

El script ejecuta tres patrones de testing async de forma secuencial, mostrando
el output real de pytest en cada uno.

**Qué hace `_run_pytest()` y por qué usa directorio temporal:**
La función escribe el test en un archivo `test_demo.py` en un directorio temporal
del sistema (`tempfile.TemporaryDirectory`) y lanza pytest sobre ese archivo via
`subprocess.run()`. Se usa un directorio temporal para no contaminar el proyecto
con archivos de test descartables. El directorio se borra automáticamente al
salir del `with`.

**Por qué `conftest.py` registra el plugin anyio explícitamente:**
El `conftest.py` del proyecto en `tests/` no está en el path cuando pytest corre
en un directorio temporal. Sin `pytest_plugins = ("anyio",)`, el marker
`@pytest.mark.anyio` no existe y pytest falla con "unknown mark". Una línea en
el conftest temporal es suficiente para registrar el plugin.

**Qué hace `assert_awaited_once_with()` y cuándo usarlo:**
Verifica dos cosas a la vez: que la coroutine fue llamada exactamente una vez y
que fue `await`-eada con los argumentos especificados. Se usa cuando la función
bajo test es un orquestador: no nos interesa su implementación interna, sino que
llame a sus dependencias con los datos correctos.

**Conexión con los tests reales del proyecto:**
Los tests en `tests/unit/` usan exactamente los mismos patrones: `@pytest.mark.anyio`,
`AsyncMock` para el cliente httpx, y `assert_awaited_once` para verificar que
`get_weather` y `get_route` se llaman desde el orquestador.

▶ Los tests async del proyecto están en `tests/unit/`:
  uv run pytest tests/ -v
