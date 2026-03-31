# Clase 05 — Concurrencia Estructurada con async/await y anyio

---

## 1. Concurrencia vs Paralelismo

### La diferencia conceptual

**Concurrencia** es sobre estructura: múltiples tareas progresan de forma intercalada,
pero no necesariamente al mismo tiempo. Una tarea se pausa mientras espera (por ejemplo,
una respuesta de red), y otra avanza mientras tanto.

**Paralelismo** es sobre ejecución simultánea: múltiples tareas corren literalmente al
mismo tiempo en distintos núcleos del procesador.

Un cocinero que enciende el horno, espera que caliente, y mientras corta verduras, está
siendo **concurrente**. Dos cocineros en cocinas separadas, cada uno preparando un plato
diferente al mismo tiempo, son **paralelos**.

### El GIL de Python: por qué async funciona para I/O

Python tiene el **GIL** (Global Interpreter Lock): un mecanismo que impide que dos hilos
ejecuten bytecode de Python al mismo tiempo dentro de un mismo proceso. Esto limita el
paralelismo real para código CPU-bound.

Sin embargo, el GIL se libera automáticamente durante operaciones de I/O (lectura de
red, disco, etc.). Mientras un hilo espera que llegue la respuesta HTTP, el GIL queda
libre para que otro hilo avance.

`async/await` aprovecha exactamente esto: cede el control en los puntos de espera de
I/O, sin necesidad de múltiples hilos ni procesos.

### Cuándo usar cada herramienta

| Caso de uso | Herramienta recomendada |
|-------------|------------------------|
| Múltiples peticiones HTTP, I/O de red | `async/await` |
| I/O de disco, múltiples tareas de espera | `async/await` |
| Cálculos intensivos (CPU-bound) | `multiprocessing` |
| Librerías síncronas de terceros en paralelo | `threading` |
| Código ya asíncrono (frameworks como FastAPI) | `async/await` (nativo) |

La regla general: si tu código pasa más tiempo **esperando** que **calculando**, async
es la herramienta correcta.

▶ Ejecuta el ejemplo:
  uv run scripts/clase_05/conceptos/01_async_await_basico.py

---

## 2. async/await en Python

### Qué es una coroutine

`async def` define una **coroutine function**. Cuando la llamas, no ejecuta el cuerpo:
retorna un objeto `coroutine`. El cuerpo solo se ejecuta cuando alguien lo espera.

```python
async def saludar(nombre: str) -> str:
    return f"Hola, {nombre}"

resultado = saludar("Ana")  # NO ejecuta nada — retorna <coroutine object>
print(resultado)             # <coroutine object saludar at 0x...>
```

Para ejecutar la coroutine, necesitas un **event loop** que la planifique y un `await`
que la espere:

```python
import anyio

async def main() -> None:
    mensaje = await saludar("Ana")  # ahora sí ejecuta
    print(mensaje)                  # Hola, Ana

anyio.run(main)
```

### await — ceder el control al event loop

`await` hace dos cosas:

1. Inicia la ejecución de la coroutine indicada.
2. Suspende la coroutine actual hasta que la otra termine, **devolviendo el control al
   event loop** para que planifique otras tareas mientras espera.

```python
import anyio

async def tarea_lenta() -> str:
    await anyio.sleep(1)  # suspende esta coroutine 1 segundo
    return "listo"

async def main() -> None:
    resultado = await tarea_lenta()
    print(resultado)

anyio.run(main)
```

Durante el `await anyio.sleep(1)`, el event loop puede ejecutar otras coroutines. Eso
es la concurrencia.

### anyio.run() como punto de entrada

`anyio.run()` es la forma de lanzar el event loop desde código síncrono. Recibe la
coroutine principal y la ejecuta hasta que termina:

```python
import anyio

async def main() -> None:
    print("inicio")
    await anyio.sleep(0.1)
    print("fin")

anyio.run(main)  # bloquea hasta que main() termina
```

Solo se llama una vez, como punto de entrada del programa. Dentro de una coroutine ya
en ejecución, no vuelves a llamar `anyio.run()`.

### Error común: olvidar await

Si llamas a una coroutine sin `await`, Python no lanza un error inmediato: simplemente
retorna el objeto coroutine sin ejecutarlo. Python sí emitirá un `RuntimeWarning`, pero
el comportamiento silencioso hace que este bug sea difícil de rastrear.

```python
async def obtener_valor() -> int:
    await anyio.sleep(0)
    return 42

async def main() -> None:
    # MAL — resultado es un objeto coroutine, no 42
    resultado = obtener_valor()
    print(resultado)   # <coroutine object obtener_valor at 0x...>
    # RuntimeWarning: coroutine 'obtener_valor' was never awaited

    # BIEN — resultado es 42
    resultado = await obtener_valor()
    print(resultado)   # 42
```

Regla: si una función es `async def`, siempre se llama con `await`.

▶ Ejecuta el ejemplo:
  uv run scripts/clase_05/conceptos/01_async_await_basico.py

---

## 3. anyio — Concurrencia Estructurada

### Por qué anyio

Python tiene `asyncio` en la librería estándar, y existe también `trio`, una alternativa
con principios de diseño más estrictos. `anyio` es una capa de compatibilidad sobre
ambos: escribe tu código una vez, y funciona sobre cualquiera de los dos backends.

Las razones prácticas para usar `anyio`:

- **Backend agnostic**: funciona con `asyncio` (default) y con `trio`.
- **API ergonómica**: `create_task_group()` es más claro que `asyncio.gather()`.
- **Compatible con FastAPI**: FastAPI usa `anyio` internamente; tu código async se
  integra sin fricciones.
- **Concurrencia estructurada**: las tareas hijas no pueden escapar de su scope.

### create_task_group() — tareas que no se escapan

La concurrencia estructurada significa que las tareas hijas viven dentro del scope
que las creó. Cuando el bloque `async with create_task_group()` termina, todas las
tareas hijas han terminado (o han fallado). No hay tareas "flotando" en el background.

```python
import anyio

async def tarea(nombre: str, segundos: float) -> None:
    await anyio.sleep(segundos)
    print(f"{nombre} terminó tras {segundos}s")

async def main() -> None:
    async with anyio.create_task_group() as tg:
        tg.start_soon(tarea, "A", 2)
        tg.start_soon(tarea, "B", 1)
        tg.start_soon(tarea, "C", 3)
    # aquí, las tres tareas han terminado
    print("todas terminaron")

anyio.run(main)
# B terminó tras 1s
# A terminó tras 2s
# C terminó tras 3s
# todas terminaron
```

El tiempo total es aproximadamente 3 segundos (el máximo), no 6 (la suma). Las tres
tareas corren de forma concurrente.

### Patrón del dict compartido para recoger resultados

`start_soon()` no retorna el valor de la tarea. Para recoger resultados, el patrón
habitual es pasar un diccionario compartido que cada tarea rellena:

```python
import anyio

async def obtener_dato(clave: str, resultados: dict[str, int]) -> None:
    await anyio.sleep(0.5)            # simula I/O
    resultados[clave] = len(clave)    # escribe el resultado

async def main() -> None:
    resultados: dict[str, int] = {}
    async with anyio.create_task_group() as tg:
        tg.start_soon(obtener_dato, "python", resultados)
        tg.start_soon(obtener_dato, "async", resultados)
        tg.start_soon(obtener_dato, "anyio", resultados)
    # el dict está completo aquí
    print(resultados)  # {'python': 6, 'async': 5, 'anyio': 5}

anyio.run(main)
```

### Error handling: ExceptionGroup

Si una tarea lanza una excepción, el task group cancela las demás tareas y propaga el
error. Si múltiples tareas fallan, las excepciones se agrupan en un `ExceptionGroup`
(introducido en Python 3.11):

```python
import anyio

async def tarea_que_falla(nombre: str) -> None:
    await anyio.sleep(0.1)
    raise ValueError(f"fallo en {nombre}")

async def main() -> None:
    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(tarea_que_falla, "A")
            tg.start_soon(tarea_que_falla, "B")
    except* ValueError as eg:
        for exc in eg.exceptions:
            print(f"capturada: {exc}")

anyio.run(main)
```

La sintaxis `except*` (Python 3.11+) maneja `ExceptionGroup`. En versiones anteriores,
`anyio` envuelve las excepciones de forma compatible.

▶ Ejecuta el ejemplo:
  uv run scripts/clase_05/conceptos/02_anyio_task_group.py

---

## 4. httpx.AsyncClient — Cliente HTTP Asíncrono

### Diferencia con httpx.Client

`httpx` ofrece dos interfaces:

- `httpx.Client` — síncrona. Los métodos `get()`, `post()`, etc. bloquean el hilo
  hasta recibir la respuesta.
- `httpx.AsyncClient` — asíncrona. Los métodos son coroutines: deben llamarse con
  `await` y ceden el control al event loop mientras esperan.

```python
# Síncrono — bloquea el hilo
import httpx

with httpx.Client() as client:
    respuesta = client.get("https://httpbin.org/get")
    datos = respuesta.json()

# Asíncrono — cede el control mientras espera
import httpx
import anyio

async def main() -> None:
    async with httpx.AsyncClient() as client:
        respuesta = await client.get("https://httpbin.org/get")
        datos = respuesta.json()

anyio.run(main)
```

La interfaz es casi idéntica; la diferencia está en `async with` y `await`.

### async with httpx.AsyncClient()

`httpx.AsyncClient` es un context manager asíncrono. Al usarlo con `async with`,
garantiza que la conexión se cierra correctamente al salir del bloque, incluso si
ocurre una excepción:

```python
async def obtener_json(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        respuesta = await client.get(url)
        respuesta.raise_for_status()
        return respuesta.json()
```

Si necesitas hacer múltiples requests en la misma función, usa el mismo cliente:
no crees uno nuevo por cada llamada.

### Connection pooling en modo async

`httpx.AsyncClient` mantiene un **pool de conexiones**: reutiliza las conexiones TCP
abiertas en lugar de crear una nueva para cada request. Esto reduce la latencia y el
consumo de recursos.

Cuando usas `AsyncClient` dentro de un task group para hacer múltiples requests
concurrentes, todas esas requests comparten el pool:

```python
async def main() -> None:
    resultados: dict[str, dict] = {}

    async def fetch(nombre: str, url: str, client: httpx.AsyncClient) -> None:
        respuesta = await client.get(url)
        resultados[nombre] = respuesta.json()

    async with httpx.AsyncClient() as client:
        async with anyio.create_task_group() as tg:
            tg.start_soon(fetch, "a", "https://httpbin.org/get?q=1", client)
            tg.start_soon(fetch, "b", "https://httpbin.org/get?q=2", client)
            tg.start_soon(fetch, "c", "https://httpbin.org/get?q=3", client)

anyio.run(main)
```

▶ Ejecuta el ejemplo:
  uv run scripts/clase_05/conceptos/03_httpx_async_client.py

---

## 5. Benchmark: Síncrono vs Asíncrono

### Por qué async es más rápido para I/O bound

Cuando haces múltiples peticiones HTTP de forma **secuencial**, el tiempo total es la
suma de todos los tiempos individuales: si cada request tarda 300ms y haces 5, esperas
1.5 segundos.

Con async y un task group, las peticiones se lanzan de forma **concurrente**: mientras
una espera la respuesta, las otras también están esperando en paralelo. El tiempo total
se aproxima al máximo de los tiempos individuales: esos mismos 5 requests tardan
aproximadamente 300ms.

```
Secuencial:  |--req1--|--req2--|--req3--|--req4--|--req5--|
             0ms                                        1500ms

Concurrente: |--req1--|
             |--req2--|
             |--req3--|
             |--req4--|
             |--req5--|
             0ms      300ms
```

### Secuencial: tiempo = suma

```python
import time
import httpx

URLS = [f"https://httpbin.org/delay/0.3" for _ in range(5)]

inicio = time.perf_counter()
with httpx.Client() as client:
    for url in URLS:
        client.get(url)
total = time.perf_counter() - inicio
print(f"Secuencial: {total:.2f}s")  # ~1.5s
```

### Concurrente: tiempo ≈ máximo

```python
import time
import httpx
import anyio

async def main() -> None:
    async def fetch(url: str, client: httpx.AsyncClient) -> None:
        await client.get(url)

    inicio = time.perf_counter()
    async with httpx.AsyncClient() as client:
        async with anyio.create_task_group() as tg:
            for url in URLS:
                tg.start_soon(fetch, url, client)
    total = time.perf_counter() - inicio
    print(f"Concurrente: {total:.2f}s")  # ~0.3s

anyio.run(main)
```

La diferencia crece con el número de requests: a 20 requests de 300ms cada una,
secuencial tarda 6 segundos; concurrente sigue tardando ~300ms.

▶ Ejecuta el ejemplo:
  uv run scripts/clase_05/conceptos/04_sync_vs_async_benchmark.py

---

## 6. Tests Async con @pytest.mark.anyio

### Por qué los tests síncronos no funcionan con funciones async

Un test síncrono que llama a una coroutine sin `await` obtiene un objeto coroutine,
no el resultado:

```python
# MAL — test síncrono con función async
def test_mi_funcion_asincrona():
    resultado = mi_funcion_async()  # retorna <coroutine>, no ejecuta nada
    assert resultado == "esperado"  # siempre falla — compara coroutine con string
```

Para ejecutar una coroutine en un test, necesitas un event loop. `pytest-anyio` lo
gestiona automáticamente con el marker `@pytest.mark.anyio`.

### @pytest.mark.anyio + async def test

```python
import pytest
import anyio

async def sumar_con_delay(a: int, b: int) -> int:
    await anyio.sleep(0)  # simula I/O asíncrono
    return a + b

@pytest.mark.anyio
async def test_suma_asincrona():
    resultado = await sumar_con_delay(2, 3)
    assert resultado == 5
```

pytest-anyio crea un event loop para el test, ejecuta la coroutine, y lo cierra al
finalizar. Cada test tiene su propio event loop limpio.

### AsyncMock — mockear funciones y context managers async

`unittest.mock.AsyncMock` es el equivalente asíncrono de `MagicMock`. Se usa para
reemplazar coroutines y context managers async en los tests:

```python
from unittest.mock import AsyncMock, MagicMock
import pytest

@pytest.mark.anyio
async def test_con_async_mock(mocker):
    # Mockear una coroutine
    mock_fetch = AsyncMock(return_value={"dato": 42})
    mocker.patch("mi_modulo.fetch_datos", mock_fetch)

    resultado = await mi_modulo.fetch_datos("url")
    assert resultado == {"dato": 42}
    mock_fetch.assert_awaited_once_with("url")
```

Para mockear un `async with` (context manager asíncrono), configura `__aenter__` y
`__aexit__`:

```python
mock_client = AsyncMock()
mock_client.__aenter__.return_value = mock_client
mock_client.__aexit__.return_value = None
mock_client.get.return_value = MagicMock(json=lambda: {"ok": True})
```

`mocker.patch` de `pytest-mock` detecta automáticamente si el objeto a parchear es
asíncrono y crea un `AsyncMock` en lugar de un `MagicMock`.

### Qué mockear cuando se testa un orquestador

Un **orquestador** es una función que coordina otras funciones: lanza tareas en
paralelo, recoge resultados, maneja errores. Al testarlo, no quieres mockear `httpx`
directamente —eso es detallar de implementación que puede cambiar. Quieres mockear
las funciones que el orquestador llama.

```python
# orquestador.py
async def obtener_multiples(claves: list[str]) -> dict[str, str]:
    resultados: dict[str, str] = {}
    async with anyio.create_task_group() as tg:
        for clave in claves:
            tg.start_soon(obtener_uno, clave, resultados)
    return resultados
```

```python
# test_orquestador.py
import pytest
from unittest.mock import AsyncMock

@pytest.mark.anyio
async def test_obtener_multiples(mocker):
    # Mockear obtener_uno — no httpx, no el cliente
    async def fake_obtener(clave: str, resultados: dict) -> None:
        resultados[clave] = f"valor-{clave}"

    mocker.patch("orquestador.obtener_uno", side_effect=fake_obtener)

    resultado = await obtener_multiples(["a", "b"])
    assert resultado == {"a": "valor-a", "b": "valor-b"}
```

Al mockear la función importada (no la librería externa), el test verifica la lógica
de coordinación del orquestador sin depender de la implementación interna de cada tarea.

▶ Ejecuta el ejemplo:
  uv run scripts/clase_05/conceptos/05_tests_async.py
