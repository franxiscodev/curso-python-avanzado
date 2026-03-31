# Lab — Clase 12: API REST con FastAPI

## Objetivo

Exponer `CommuteService` como API REST HTTP usando FastAPI.
Al final de este lab, cualquier cliente HTTP podrá consultar rutas,
listar ciudades y ver el historial — sin importar en qué lenguaje esté escrito.

## Prerrequisitos

- Clase 11 completada — `CommuteService` con `FallbackAIAdapter`
- Snapshot `snapshots/clase_11/` como referencia

## Nuevas dependencias

```bash
# Windows (PowerShell) — desde la raíz del repo
uv add "fastapi>=0.111" "uvicorn[standard]>=0.30"

# Linux — desde la raíz del repo
uv add "fastapi>=0.111" "uvicorn[standard]>=0.30"
```

---

## Paso 1 — Schemas HTTP (DTOs)

Crea `src/pycommute/api/schemas.py`.

Este archivo define los contratos de entrada y salida de la API.
Son DTOs (Data Transfer Objects) — distintos de los modelos de dominio en `core/`.

```python
# src/pycommute/api/schemas.py
from pydantic import BaseModel, Field

from pycommute.core.models import RouteData, WeatherData


class CommuteRequest(BaseModel):
    origin_city: str = Field(min_length=1, examples=["Valencia"])
    destination_city: str = Field(min_length=1, examples=["Madrid"])
    profiles: list[str] = Field(
        default=["driving-car", "cycling-regular"],
        examples=[["driving-car", "cycling-regular"]],
    )
    include_ai: bool = Field(default=True, description="Incluir recomendacion de IA")


class AIRecommendation(BaseModel):
    recommendation: str
    confidence: str


class CommuteResponse(BaseModel):
    origin_city: str
    destination_city: str
    origin_weather: WeatherData
    destination_weather: WeatherData
    routes: list[RouteData]
    best_route: RouteData | None
    ai_recommendation: AIRecommendation | None = None


class HistoryEntry(BaseModel):
    timestamp: str
    origin_city: str
    profiles: list[str]
    best_profile: str | None


class HealthResponse(BaseModel):
    status: str
    version: str
    adapters: dict[str, str]


class CitiesResponse(BaseModel):
    cities: list[str]
    total: int
```

Aplica: sección "Pydantic en FastAPI" de `01_conceptos.md`.

---

## Paso 2 — Dependencias inyectables

Crea `src/pycommute/api/dependencies.py`.

```python
# src/pycommute/api/dependencies.py
from functools import lru_cache

from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.adapters.fallback_ai import FallbackAIAdapter
from pycommute.adapters.gemini import GeminiAdapter
from pycommute.adapters.ollama_adapter import OllamaAdapter
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.services.commute import CommuteService


def get_settings():
    """Dependencia que expone Settings — sobreescribible en tests."""
    from pycommute.config import settings
    return settings


@lru_cache
def get_commute_service() -> CommuteService:
    """Factory cacheada del CommuteService con todos sus adaptadores."""
    cfg = get_settings()
    ai_adapter = FallbackAIAdapter(
        primary=GeminiAdapter(
            api_key=cfg.google_api_key,
            model=cfg.gemini_model,
        ),
        secondary=OllamaAdapter(
            model=cfg.ollama_model,
            base_url=cfg.ollama_base_url,
        ),
    )
    return CommuteService(
        weather=OpenWeatherAdapter(),
        route=OpenRouteAdapter(),
        cache=MemoryCacheAdapter(),
        ai=ai_adapter,
    )
```

Aplica: sección "lru_cache con Depends" de `01_conceptos.md`.

**Nota sobre `get_settings()`:** El import de `settings` está dentro de la
función, no a nivel de módulo. Así los tests pueden ejecutarse sin `.env`.

---

## Paso 3 — Routers

Crea los tres routers en `src/pycommute/api/routers/`.

### health.py

```python
# src/pycommute/api/routers/health.py
from fastapi import APIRouter

from pycommute import __version__
from pycommute.api.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=__version__,
        adapters={
            "weather": "OpenWeatherAdapter",
            "route": "OpenRouteAdapter",
            "ai": "FallbackAIAdapter(Gemini + Ollama)",
            "cache": "MemoryCacheAdapter",
        },
    )
```

### cities.py

```python
# src/pycommute/api/routers/cities.py
from fastapi import APIRouter

from pycommute.adapters.cache import _COORDENADAS
from pycommute.api.schemas import CitiesResponse

router = APIRouter()


@router.get("/cities", response_model=CitiesResponse)
async def list_cities() -> CitiesResponse:
    cities = sorted(_COORDENADAS.keys())
    return CitiesResponse(cities=cities, total=len(cities))
```

### commute.py

```python
# src/pycommute/api/routers/commute.py
from fastapi import APIRouter, Depends, HTTPException

from pycommute.api.dependencies import get_commute_service, get_settings
from pycommute.api.schemas import CommuteRequest, CommuteResponse, HistoryEntry
from pycommute.services.commute import CommuteService

router = APIRouter(prefix="/commute")


@router.post("/", response_model=CommuteResponse)
async def get_commute(
    request: CommuteRequest,
    service: CommuteService = Depends(get_commute_service),
    cfg=Depends(get_settings),
) -> CommuteResponse:
    try:
        result = await service.get_commute_info(
            city=request.origin_city,
            destination_city=request.destination_city,
            profiles=request.profiles,
            weather_key=cfg.openweather_api_key,
            route_key=cfg.openrouteservice_api_key,
            google_key=cfg.google_api_key if request.include_ai else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return CommuteResponse(**result.model_dump())


@router.get("/history", response_model=list[HistoryEntry])
async def get_history(
    n: int = 10,
    service: CommuteService = Depends(get_commute_service),
) -> list[HistoryEntry]:
    entries = service.history.get_recent(n)
    return [
        HistoryEntry(
            timestamp=e.timestamp.isoformat(),
            origin_city=e.city,
            profiles=e.profiles,
            best_profile=e.result.best_route.profile if e.result.best_route else None,
        )
        for e in entries
    ]
```

Aplica: secciones "APIRouter" y "Depends()" de `01_conceptos.md`.

---

## Paso 4 — Main app con lifespan

Crea `src/pycommute/api/main.py`.

```python
# src/pycommute/api/main.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from pycommute import __version__
from pycommute.api.routers import cities, commute, health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("PyCommute API v{version} iniciando...", version=__version__)
    yield
    logger.info("PyCommute API cerrando...")


app = FastAPI(
    title="PyCommute API",
    description="Asesor de movilidad inteligente con IA hibrida (Gemini + Ollama fallback)",
    version=__version__,
    lifespan=lifespan,
)

app.include_router(health.router, tags=["health"])
app.include_router(cities.router, tags=["cities"])
app.include_router(commute.router, tags=["commute"])
```

Crea también `src/pycommute/api/__init__.py` y
`src/pycommute/api/routers/__init__.py` vacíos.

Aplica: sección "Lifespan" de `01_conceptos.md`.

---

## Paso 5 — Verificar que el servidor arranca

```bash
# Windows (PowerShell) — desde curso/
cd curso
uvicorn pycommute.api.main:app --reload --port 8000

# Linux — desde curso/
cd curso
uvicorn pycommute.api.main:app --reload --port 8000
```

Abre `http://localhost:8000/docs` en el browser.

Deberías ver:
- Sección `health` → `GET /health`
- Sección `cities` → `GET /cities`
- Sección `commute` → `POST /commute/` y `GET /commute/history`

Ejecuta `GET /health` desde Swagger UI — debe devolver `{"status": "ok", ...}`.

---

## Paso 6 — Tests de integración

Crea `tests/integration/test_api.py`.

```python
# tests/integration/test_api.py
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from pycommute.api.dependencies import get_commute_service, get_settings
from pycommute.api.main import app
from pycommute.core.models import CommuteResult, RouteData, WeatherData

_MOCK_RESULT = CommuteResult(
    origin_city="Valencia",
    destination_city="Madrid",
    origin_weather=WeatherData(city="Valencia", temperature=20.0,
                               description="Soleado", humidity=50, wind_speed=5.0),
    destination_weather=WeatherData(city="Madrid", temperature=18.0,
                                    description="Nublado", humidity=60, wind_speed=8.0),
    routes=[RouteData(profile="driving-car", distance_km=350.0,
                      duration_min=180.0, summary="A-3")],
    best_route=RouteData(profile="driving-car", distance_km=350.0,
                         duration_min=180.0, summary="A-3"),
    ai_recommendation=None,
)


def _mock_service() -> MagicMock:
    service = MagicMock()
    service.history.get_recent.return_value = []
    service.get_commute_info = AsyncMock(return_value=_MOCK_RESULT)
    return service


def _mock_settings() -> MagicMock:
    cfg = MagicMock()
    cfg.openweather_api_key = "test-weather-key"
    cfg.openrouteservice_api_key = "test-route-key"
    cfg.google_api_key = "test-google-key"
    return cfg


app.dependency_overrides[get_commute_service] = _mock_service
app.dependency_overrides[get_settings] = _mock_settings

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_cities_returns_list():
    response = client.get("/cities")
    assert response.status_code == 200
    data = response.json()
    assert "cities" in data
    assert data["total"] > 0


def test_commute_returns_result():
    response = client.post("/commute/", json={
        "origin_city": "Valencia",
        "destination_city": "Madrid",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["origin_city"] == "Valencia"
    assert len(data["routes"]) > 0


def test_commute_invalid_origin_city():
    response = client.post("/commute/", json={
        "origin_city": "",
        "destination_city": "Madrid",
    })
    assert response.status_code == 422


def test_history_returns_list():
    response = client.get("/commute/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

Aplica: sección "Testing con TestClient" de `01_conceptos.md`.

---

## Ejecutar los tests

```bash
# Windows (PowerShell) — desde la raíz del repo
uv run pytest curso/tests/ -v

# Linux — desde la raíz del repo
uv run pytest curso/tests/ -v
```

Resultado esperado: **57 tests pasan** (52 unit + 5 integration).

---

## Demo del servidor completo

```bash
# Windows (PowerShell) — desde la raíz del repo
uv run python curso/scripts/clase_12/demo_proyecto.py

# Linux — desde la raíz del repo
uv run python curso/scripts/clase_12/demo_proyecto.py
```

El script arranca el servidor, hace consultas reales y lo para.

---

## ¿Por qué construimos esto así?

### La arquitectura hexagonal pagó su deuda

En Clase 8 definimos puertos con `Protocol`.
En Clase 9 añadimos contratos Pydantic.
En Clases 10 y 11 conectamos Gemini y Ollama como adaptadores.

En esta clase **no tocamos ninguno de esos módulos**.
`core/`, `adapters/`, `services/` quedan intactos.
Solo añadimos una nueva capa: `api/`.

Eso es exactamente lo que prometió la arquitectura hexagonal:
agregar un adaptador HTTP sin modificar el negocio.

### Por qué DTOs separados del modelo de dominio

`CommuteResult` vive en `core/` y habla el lenguaje del negocio.
`CommuteRequest` y `CommuteResponse` hablan el lenguaje de HTTP.

Si mañana la API cambia (nuevos campos, versioning), solo cambian los DTOs.
Si mañana el dominio cambia (nueva lógica de rutas), solo cambia `CommuteResult`.
Cada capa cambia por sus propias razones — sin arrastrar a la otra.

### Por qué `get_settings()` como dependencia

El import de `settings` a nivel de módulo falla en tests porque no hay `.env`
en el directorio de trabajo cuando pytest corre desde la raíz.

`get_settings()` como dependencia FastAPI permite dos cosas:
1. El import ocurre en tiempo de request, no de módulo — pytest no explota
2. Los tests pueden inyectar `_mock_settings()` via `dependency_overrides` — sin archivos `.env`, sin `mocker.patch`

### Por qué tres routers en lugar de un archivo

Con tres endpoints ya vale la pena separar.
En proyectos reales los routers crecen hasta tener 10-20 endpoints.
Aprender el patrón antes de necesitarlo evita refactorizaciones urgentes.

### Lo que viene

En Clase 13 Docker Compose empaqueta esta API junto con Gradio.
El código de esta clase no cambia — solo el contexto de ejecución.
Las variables de entorno vienen del `docker-compose.yml` en lugar del `.env`.

---

## Snapshot del hito

El estado de esta clase está preservado en:

```
snapshots/clase_12/src/pycommute/api/
snapshots/clase_12/tests/integration/
```

Úsalo como referencia si algo no funciona.
