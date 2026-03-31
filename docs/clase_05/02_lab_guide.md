# Lab Guide — Clase 5: Concurrencia Estructurada

## ¿Por qué construimos esto así?

Hacer una función `async def` no es suficiente para que las llamadas se
ejecuten en paralelo. Sin `anyio.create_task_group()`, dos funciones `async`
llamadas una tras otra siguen siendo secuenciales: `await weather()` bloquea
hasta terminar, y solo entonces empieza `await route()`. La concurrencia real
requiere un orquestador que las lance juntas.

Por eso creamos `commute.py` como módulo separado en lugar de poner la
orquestación directamente en `weather.py` o `route.py`. Cada módulo tiene
una responsabilidad única: `weather.py` consulta el clima, `route.py`
consulta la ruta, `commute.py` orquesta ambas. Esta separación no es
arbitraria: `commute.py` es la semilla del _service layer_ que formalizaremos
en la Clase 8 con arquitectura hexagonal.

En `test_commute.py` mockeamos las funciones importadas (`get_current_weather`,
`get_route`) en lugar de mockear `httpx.AsyncClient`. La razón es técnica: si
parcheáramos `httpx.AsyncClient` dos veces — una para weather y otra para
route — el segundo `patch` sobreescribiría al primero, porque ambos módulos
comparten el mismo objeto en memoria. Mockear las funciones directamente evita
ese problema y además hace los tests más legibles: el contrato que verificamos
es "commute llama a weather y a route con los argumentos correctos", no "commute
abre dos conexiones HTTP".

Usamos `anyio` en lugar de `asyncio` puro porque ya está en el stack del
proyecto y es compatible con FastAPI (Clase 12), lo que nos evita cambiar de
event loop más adelante.

---

## Dependencias de esta clase

```bash
# Windows (PowerShell) y Linux (idéntico)
uv add "anyio>=4.4"
```

Verifica que `pyproject.toml` incluye `anyio` bajo el comentario
`# Clase 5 — concurrencia estructurada` en la sección `[project] dependencies`.

---

## Pasos del lab

### Paso 1 — Verificar `anyio` en `pyproject.toml`

Abre `pyproject.toml` y confirma que la sección de dependencias contiene:

```toml
dependencies = [
    # Clase 1 — cliente HTTP y variables de entorno
    "httpx>=0.27",
    "python-dotenv>=1.0",

    # Clase 3 — resiliencia profesional
    "loguru>=0.7",
    "pydantic-settings>=2.0",
    "tenacity>=8.0",

    # Clase 5 — concurrencia estructurada
    "anyio>=4.4",
]
```

Si el comentario `# Clase 5` no aparece, agrégalo junto a la dependencia.

---

### Paso 2 — Migrar `weather.py` a `async`

Aplicamos la sección "Funciones `async def` y `await`" de `01_conceptos.md`.

Los tres cambios son mecánicos y sistemáticos:

| Antes | Después |
|---|---|
| `def get_current_weather(...)` | `async def get_current_weather(...)` |
| `httpx.Client()` | `httpx.AsyncClient()` |
| `client.get(...)` | `await client.get(...)` |

El bloque de contexto también cambia:

```python
# Antes
with httpx.Client() as client:
    response = client.get(url, params=params)

# Después
async with httpx.AsyncClient() as client:
    response = await client.get(url, params=params)
```

La firma de la función completa queda:

```python
async def get_current_weather(
    city: str,
    api_key: str,
) -> dict:
```

---

### Paso 3 — Migrar `route.py` a `async`

Aplicamos el mismo patrón que en el Paso 2.

Cambia `def` → `async def`, `httpx.Client` → `httpx.AsyncClient`,
y `client.get(...)` → `await client.get(...)`.

---

### Paso 4 — Verificar que los tests existentes FALLAN

Ejecuta la suite antes de actualizar los tests:

```bash
# Windows (PowerShell)
uv run pytest tests/ -v

# Linux
uv run pytest tests/ -v
```

Esperamos ver errores similares a:

```
RuntimeWarning: coroutine 'get_current_weather' was never awaited
```

Esto confirma que la migración a `async` fue correcta y que los tests de
Clase 4 aún no saben cómo llamar funciones asíncronas. El Paso 5 lo resuelve.

---

### Paso 5 — Actualizar `conftest.py` con `AsyncMock`

Aplicamos la sección "`AsyncMock` y mocks de clientes asíncronos" de
`01_conceptos.md`.

Abre `curso/tests/conftest.py` y reemplaza `MagicMock(spec=httpx.AsyncClient)`
por `AsyncMock()`, y actualiza los patches para apuntar a `httpx.AsyncClient`
en lugar de `httpx.Client`:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_client_weather(mocker):
    """AsyncMock de httpx.AsyncClient para llamadas a OpenWeatherMap."""
    mock = AsyncMock()
    mocker.patch("pycommute.weather.httpx.AsyncClient", return_value=mock)
    return mock

@pytest.fixture
def mock_client_route(mocker):
    """AsyncMock de httpx.AsyncClient para llamadas a OpenRouteService."""
    mock = AsyncMock()
    mocker.patch("pycommute.route.httpx.AsyncClient", return_value=mock)
    return mock
```

> `AsyncMock` hace que `await mock.get(...)` funcione y devuelva otro mock
> awaitable, sin lanzar `TypeError`.

---

### Paso 6 — Actualizar `test_weather.py` con `@pytest.mark.anyio`

Aplicamos la sección "Tests asíncronos con `pytest-anyio`" de `01_conceptos.md`.

Cada test en `curso/tests/unit/test_weather.py` necesita dos cambios:

1. El decorador `@pytest.mark.anyio` sobre la función.
2. La firma `async def` en lugar de `def`.
3. `await` en la llamada a `get_current_weather(...)`.

Ejemplo del primer test tras la migración:

```python
import pytest
from pycommute.weather import get_current_weather

@pytest.mark.anyio
async def test_weather_valid_response(mock_client_weather):
    mock_client_weather.get.return_value.json.return_value = {
        "main": {"temp": 22.5},
        "weather": [{"description": "clear sky"}],
    }
    mock_client_weather.get.return_value.raise_for_status.return_value = None

    result = await get_current_weather("Madrid", api_key="test-key")

    assert result["temp"] == 22.5
    assert result["description"] == "clear sky"
```

Aplica el mismo patrón a los 5 tests: añade `@pytest.mark.anyio`,
`async def`, y `await` en la llamada.

---

### Paso 7 — Actualizar `test_route.py` con `@pytest.mark.anyio`

Mismo patrón que el Paso 6.

Añade `@pytest.mark.anyio`, `async def` y `await` en la llamada a
`get_route(...)` en los 5 tests de `curso/tests/unit/test_route.py`.

---

### Paso 8 — Crear `commute.py`

Aplicamos la sección "`anyio.create_task_group()` y paralelismo estructurado"
de `01_conceptos.md`.

Crea `curso/src/pycommute/commute.py` con la función `get_commute_info()`:

```python
import anyio
from pycommute.weather import get_current_weather
from pycommute.route import get_route


async def get_commute_info(
    city: str,
    origin: tuple[float, float],
    destination: tuple[float, float],
    weather_api_key: str,
    route_api_key: str,
    profile: str = "foot-walking",
) -> dict:
    """Obtiene clima y ruta en paralelo usando anyio.create_task_group().

    Args:
        city: Nombre de la ciudad para la consulta de clima.
        origin: Coordenadas (lat, lon) del punto de partida.
        destination: Coordenadas (lat, lon) del destino.
        weather_api_key: API key de OpenWeatherMap.
        route_api_key: API key de OpenRouteService.
        profile: Perfil de ruta (foot-walking, driving-car, cycling-regular).

    Returns:
        Diccionario con las claves "weather" y "route".
    """
    results: dict = {}

    async def fetch_weather() -> None:
        results["weather"] = await get_current_weather(city, weather_api_key)

    async def fetch_route() -> None:
        results["route"] = await get_route(origin, destination, route_api_key, profile)

    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch_weather)
        tg.start_soon(fetch_route)

    return results
```

> Las dos funciones internas comparten el diccionario `results` por closure.
> `create_task_group()` garantiza que ambas terminan (o que cualquier excepción
> se propaga correctamente) antes de continuar.

---

### Paso 9 — Crear `test_commute.py`

Aplicamos la sección "Mockear funciones importadas vs. mockear dependencias
externas" de `01_conceptos.md`.

Crea `curso/tests/unit/test_commute.py` con 2 tests. Los mocks apuntan a las
funciones importadas dentro de `commute.py`, no a `httpx`:

```python
import pytest
from unittest.mock import AsyncMock
from pycommute.commute import get_commute_info


@pytest.mark.anyio
async def test_commute_returns_weather_and_route(mocker):
    mock_weather = mocker.patch(
        "pycommute.commute.get_current_weather",
        new_callable=AsyncMock,
        return_value={"temp": 18.0, "description": "cloudy"},
    )
    mock_route = mocker.patch(
        "pycommute.commute.get_route",
        new_callable=AsyncMock,
        return_value={"distance_km": 3.2, "duration_min": 38, "profile": "foot-walking"},
    )

    result = await get_commute_info(
        city="Madrid",
        origin=(40.4168, -3.7038),
        destination=(40.4530, -3.6883),
        weather_api_key="ow-test",
        route_api_key="ors-test",
    )

    assert "weather" in result
    assert "route" in result
    assert result["weather"]["temp"] == 18.0
    assert result["route"]["distance_km"] == 3.2


@pytest.mark.anyio
async def test_commute_calls_both_functions(mocker):
    mocker.patch(
        "pycommute.commute.get_current_weather",
        new_callable=AsyncMock,
        return_value={"temp": 20.0, "description": "sunny"},
    )
    mock_route = mocker.patch(
        "pycommute.commute.get_route",
        new_callable=AsyncMock,
        return_value={"distance_km": 5.1, "duration_min": 55, "profile": "driving-car"},
    )

    await get_commute_info(
        city="Valencia",
        origin=(39.4699, -0.3763),
        destination=(39.4900, -0.3500),
        weather_api_key="ow-test",
        route_api_key="ors-test",
        profile="driving-car",
    )

    mock_route.assert_called_once()
    _, kwargs = mock_route.call_args
    assert kwargs.get("profile") == "driving-car" or mock_route.call_args[0][-1] == "driving-car"
```

> Parcheamos `pycommute.commute.get_current_weather`, no
> `pycommute.weather.get_current_weather`. El patch debe apuntar al nombre tal
> como aparece en el módulo que lo importa.

---

### Paso 10 — Verificar el hito: 19 tests en verde

```bash
# Windows (PowerShell)
uv run pytest tests/ -v

# Linux
uv run pytest tests/ -v
```

Salida esperada:

```
tests/unit/test_weather.py::test_weather_valid_response PASSED
tests/unit/test_weather.py::test_weather_http_error PASSED
tests/unit/test_weather.py::test_weather_returns_dict PASSED
tests/unit/test_weather.py::test_weather_malformed_response PASSED
tests/unit/test_weather.py::test_weather_multiple_cities[Madrid] PASSED
tests/unit/test_weather.py::test_weather_multiple_cities[Valencia] PASSED
tests/unit/test_weather.py::test_weather_multiple_cities[Bilbao] PASSED
tests/unit/test_route.py::test_route_valid_response PASSED
tests/unit/test_route.py::test_route_http_error PASSED
tests/unit/test_route.py::test_route_unit_conversion PASSED
tests/unit/test_route.py::test_route_profile_preserved PASSED
tests/unit/test_route.py::test_route_multiple_profiles[foot-walking] PASSED
tests/unit/test_route.py::test_route_multiple_profiles[driving-car] PASSED
tests/unit/test_route.py::test_route_multiple_profiles[cycling-regular] PASSED
tests/unit/test_config.py::test_settings_loads_from_env PASSED
tests/unit/test_config.py::test_settings_raises_without_required_keys PASSED
tests/unit/test_config.py::test_settings_default_values PASSED
tests/unit/test_commute.py::test_commute_returns_weather_and_route PASSED
tests/unit/test_commute.py::test_commute_calls_both_functions PASSED

19 passed in 0.45s
```

Si ves 19 tests en verde, el hito está completo.

---

### Paso 11 — Medir el benchmark

Ejecuta la demo que compara ejecución secuencial vs. paralela con APIs reales:

```bash
# Windows (PowerShell)
uv run scripts/clase_05/demo_proyecto.py

# Linux
uv run scripts/clase_05/demo_proyecto.py
```

Salida esperada (los tiempos variarán según la latencia de red):

```
Secuencial:  1.84s
Paralelo:    0.97s
Speedup:     1.9x
```

Un _speedup_ cercano a 2x confirma que las dos llamadas de red corren en
paralelo. Si ves un speedup menor a 1.3x, revisa que `commute.py` usa
`tg.start_soon()` para ambas tareas dentro del mismo `create_task_group()`.

---

## Hito de la Clase 5

Tu código y tests al terminar esta clase deben coincidir con
`curso/snapshots/clase_05/`.

```bash
# Windows (PowerShell)
uv run pytest tests/ -v

# Linux
uv run pytest tests/ -v
```

Compara tu `src/pycommute/` con `snapshots/clase_05/src/pycommute/` para
verificar que `weather.py`, `route.py` y `commute.py` tienen las firmas
`async def` correctas y que `commute.py` usa `anyio.create_task_group()`.

La Clase 6 tomará este código como punto de partida para medir dónde están
los cuellos de botella reales con profiling, y optimizar los puntos críticos
con generadores y `__slots__`.
