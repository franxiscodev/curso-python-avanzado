# Clase 08 — Lab Guide: Arquitectura Hexagonal en PyCommute

## Objetivo del lab

Reorganizar PyCommute con Arquitectura Hexagonal. Al finalizar:
- El proyecto tiene capas `core/`, `adapters/` y `services/`
- `CommuteService` recibe sus dependencias por constructor
- Los 31 tests pasan sin modificar ninguna asercion
- El output del demo es idéntico al de Clase 7

---

## Paso 0 — Revisar los conceptos

Antes del lab, ejecuta y lee los scripts de conceptos:

```bash
# Windows (PowerShell)
uv run scripts/clase_08/conceptos/01_protocol_basico.py
uv run scripts/clase_08/conceptos/02_inyeccion_dependencias.py
uv run scripts/clase_08/conceptos/03_regla_dependencia.py
uv run scripts/clase_08/conceptos/04_hexagonal_completo.py

# Linux
uv run scripts/clase_08/conceptos/01_protocol_basico.py
uv run scripts/clase_08/conceptos/02_inyeccion_dependencias.py
uv run scripts/clase_08/conceptos/03_regla_dependencia.py
uv run scripts/clase_08/conceptos/04_hexagonal_completo.py
```

Ver `01_conceptos.md` — secciones 3 a 7.

---

## Paso 1 — Crear las capas

```bash
# Windows (PowerShell)
mkdir src\pycommute\core
mkdir src\pycommute\adapters
mkdir src\pycommute\services

# Linux
mkdir -p src/pycommute/core src/pycommute/adapters src/pycommute/services
```

Crear `__init__.py` en cada directorio nuevo:

```bash
# Windows (PowerShell)
echo "" > src\pycommute\core\__init__.py
echo "" > src\pycommute\adapters\__init__.py
echo "" > src\pycommute\services\__init__.py

# Linux
touch src/pycommute/core/__init__.py
touch src/pycommute/adapters/__init__.py
touch src/pycommute/services/__init__.py
```

---

## Paso 2 — Crear core/ports.py

Aplicamos la sección 3 de `01_conceptos.md`.

```python
# src/pycommute/core/ports.py
from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class WeatherPort(Protocol):
    async def get_current_weather(self, city: str, api_key: str) -> dict[str, Any]: ...

@runtime_checkable
class RoutePort(Protocol):
    async def get_route(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        profile: str,
        api_key: str,
    ) -> dict[str, Any]: ...

@runtime_checkable
class CachePort(Protocol):
    def get_coordinates(self, city: str) -> tuple[float, float]: ...
```

**Regla:** `core/ports.py` no tiene imports del proyecto — solo stdlib.

---

## Paso 3 — Mover ranking.py y history.py a core/

```bash
# Windows (PowerShell)
move src\pycommute\ranking.py src\pycommute\core\ranking.py
move src\pycommute\history.py src\pycommute\core\history.py

# Linux
mv src/pycommute/ranking.py src/pycommute/core/ranking.py
mv src/pycommute/history.py src/pycommute/core/history.py
```

No hay cambios de código — solo de ubicación.

---

## Paso 4 — Crear adapters/weather.py

Tomamos el código de `weather.py` y lo envolvemos en una clase:

```python
# src/pycommute/adapters/weather.py
from typing import Any
import httpx
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


class OpenWeatherAdapter:
    """Adaptador concreto para la API de OpenWeatherMap.

    Implementa WeatherPort sin heredar de él — duck typing estructural.
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
        reraise=True,
    )
    async def get_current_weather(self, city: str, api_key: str) -> dict[str, Any]:
        params = {"q": city, "appid": api_key, "units": "metric"}
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
        match data:
            case {"main": {"temp": temp}, "weather": [{"description": desc}, *_]}:
                return {"temperature": temp, "description": desc, "city": city}
            case _:
                raise ValueError(f"Respuesta inesperada de OpenWeather: {data}")
```

Repite el patrón para `adapters/route.py` y `adapters/cache.py`.

---

## Paso 5 — Crear services/commute.py

Aplicamos la sección 5 de `01_conceptos.md` — constructor injection.

```python
# src/pycommute/services/commute.py
from typing import Any, AsyncGenerator
import anyio
from pycommute.core.history import ConsultaHistory
from pycommute.core.ports import CachePort, RoutePort, WeatherPort
from pycommute.core.ranking import rank_routes_by_time


class CommuteService:
    def __init__(
        self,
        weather: WeatherPort,
        route: RoutePort,
        cache: CachePort,
        history: ConsultaHistory | None = None,
    ) -> None:
        self._weather = weather
        self._route = route
        self._cache = cache
        self._history = history or ConsultaHistory()

    async def get_commute_info(
        self,
        city: str,
        destination_city: str,
        profiles: list[str],
        weather_key: str,
        route_key: str,
    ) -> dict[str, Any]:
        origin = self._cache.get_coordinates(city)
        destination = self._cache.get_coordinates(destination_city)
        results: dict[str, Any] = {}

        async def fetch_weather() -> None:
            results["weather"] = await self._weather.get_current_weather(city, weather_key)

        async def fetch_routes() -> None:
            routes = []
            async for route in self._iter_routes(origin, destination, profiles, route_key):
                routes.append(route)
            results["routes"] = rank_routes_by_time(routes)

        async with anyio.create_task_group() as tg:
            tg.start_soon(fetch_weather)
            tg.start_soon(fetch_routes)

        self._history.add(city=city, profiles=profiles,
                         weather=results["weather"], routes=results["routes"])
        return results

    async def _iter_routes(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        profiles: list[str],
        api_key: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        for profile in profiles:
            yield await self._route.get_route(origin, destination, profile, api_key)

    @property
    def history(self) -> ConsultaHistory:
        return self._history
```

---

## Paso 6 — Eliminar los archivos originales

```bash
# Windows (PowerShell)
git rm src\pycommute\weather.py
git rm src\pycommute\route.py
git rm src\pycommute\cache.py
git rm src\pycommute\commute.py

# Linux
git rm src/pycommute/weather.py
git rm src/pycommute/route.py
git rm src/pycommute/cache.py
git rm src/pycommute/commute.py
```

---

## Paso 7 — Actualizar imports en tests/

Los imports que cambian:

| Antes | Despues |
|-------|---------|
| `from pycommute.weather import ...` | `from pycommute.adapters.weather import OpenWeatherAdapter` |
| `from pycommute.route import ...` | `from pycommute.adapters.route import OpenRouteAdapter` |
| `from pycommute.cache import ...` | `from pycommute.adapters.cache import MemoryCacheAdapter, get_coordinates` |
| `from pycommute.commute import get_commute_info` | `from pycommute.services.commute import CommuteService` |
| `from pycommute.ranking import ...` | `from pycommute.core.ranking import ...` |
| `from pycommute.history import ...` | `from pycommute.core.history import ConsultaHistory` |

En `conftest.py`, actualizar los paths de `mocker.patch`:
```python
mocker.patch("pycommute.adapters.weather.httpx.AsyncClient", ...)
mocker.patch("pycommute.adapters.route.httpx.AsyncClient", ...)
```

---

## Paso 8 — Verificar el hito

```bash
# Windows (PowerShell)
uv run pytest tests/ -v
# Esperado: 31 passed

uv run scripts/clase_08/demo_proyecto.py
# Esperado:
# OpenWeatherAdapter satisface WeatherPort: True
# OpenRouteAdapter satisface RoutePort:    True
# MemoryCacheAdapter satisface CachePort:  True

# Linux — mismos comandos
```

Si hay imports rotos: `pytest` te dirá exactamente qué módulo falta.

---

## ¿Por qué construimos esto así?

### La historia de PyCommute — lo que construiste sin saberlo

**Clase 2:** Creaste `weather.py` y `route.py` separados porque "cada módulo tiene una responsabilidad". Eso era **Separacion de Responsabilidades** (S de SOLID).

**Clase 5:** `commute.py` orquestó weather y route sin mezclar la lógica de HTTP con la lógica de orquestación. Eso era la **Inversión de Dependencias** — implícita, no formalizada.

**Clase 6:** `cache.py` se separó de `commute.py` con la razón "si mañana usamos Redis, solo cambia `cache.py`". Eso era el **Principio Abierto/Cerrado** — abierto a nuevas implementaciones, cerrado a modificaciones del orquestador.

**Clase 8:** Formalizamos todo con nombres: Arquitectura Hexagonal, Puertos y Adaptadores, Inyección de Dependencias. **El código no cambia en esencia — cambia su organización y sus nombres.**

### Por qué esto importa en la práctica

Sin esta organización, agregar la integración con Gemini (Clase 10) requeriría tocar `commute.py` para cambiar los imports. Con esta organización, se crea `adapters/gemini_weather.py` y se pasa al `CommuteService` en el punto de construcción — `commute.py` no se toca.

Sin DI en los tests, el test de `CommuteService` necesitaría parchear `pycommute.weather.httpx.AsyncClient` — frágil porque depende de la ruta interna de un módulo. Con DI, el test pasa un mock directamente — robusto e independiente de la implementación interna.

---

## Snapshot de la clase

Al finalizar, el estado del proyecto está en:

```
snapshots/clase_08/
├── src/pycommute/          ← código con comentarios [CLASE 8] y [CLASE 9 →]
└── tests/                  ← tests actualizados a los nuevos imports
```

La próxima clase (Clase 9) agrega Pydantic V2 para validar los datos que fluyen entre adaptadores y servicio.
