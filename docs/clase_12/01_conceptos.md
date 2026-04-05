# Clase 12 — API REST Profesional con FastAPI

## 1. FastAPI — framework ASGI

FastAPI es un framework web async-first para Python.

**ASGI vs WSGI:**

| | WSGI (Flask, Django) | ASGI (FastAPI) |
|---|---|---|
| Modelo | Sincrono, un hilo por request | Async, event loop compartido |
| `await` nativo | No | Sí |
| WebSockets | No nativo | Soporte nativo |
| Performance I/O | Limitado por hilos | Excelente |

**Stack interno de FastAPI:**
- **Uvicorn** — servidor ASGI que ejecuta la app
- **Starlette** — routing y middleware
- **Pydantic** — validación y serialización

Los endpoints se definen con decoradores sobre el objeto `app`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/salud")
async def salud():
    return {"estado": "ok"}
```

La documentación interactiva está disponible en `/docs` (Swagger UI) y
`/redoc` sin configuración adicional — FastAPI la genera del código.

**Ejecutar una app FastAPI localmente:**

FastAPI incluye un CLI de desarrollo a través del extra `[standard]`:

```bash
# desde curso/
uv run fastapi dev scripts/clase_12/conceptos/01_fastapi_lifespan.py
```

`fastapi dev` activa hot-reload automáticamente — al guardar el archivo,
el servidor se reinicia sin Ctrl+C. El servidor arranca en
`http://localhost:8000` por defecto. Abre `/docs` para ver Swagger UI.

**Por qué `--port`:**
El puerto 8000 es el predeterminado. Si ya tienes un script corriendo,
el segundo dará error de "address already in use". Con `--port` cada script
ocupa un puerto diferente:

```bash
uv run fastapi dev scripts/clase_12/conceptos/01_fastapi_lifespan.py --port 8001
uv run fastapi dev scripts/clase_12/conceptos/02_depends_pattern.py    --port 8002
```

**`fastapi[standard]` vs `fastapi` bare:**

| Paquete | Incluye |
|---------|---------|
| `fastapi` | solo el framework (routers, Depends, Pydantic) |
| `fastapi[standard]` | + `fastapi-cli` (comando `fastapi dev/run`) |
| | + `uvicorn[standard]` (el servidor ASGI) |
| | + `python-multipart` (form data) |

El bare `fastapi` no instala el comando `fastapi` — por eso la primera vez
da error hasta añadir `fastapi[standard]`.

▶ Ejecuta el ejemplo:
  `uv run fastapi dev scripts/clase_12/conceptos/01_fastapi_lifespan.py --port 8001`
  Luego abre: `http://localhost:8001/docs`

---

## 2. Lifespan — ciclo de vida y estado global

El hook `lifespan` separa startup de shutdown con un context manager:

```python
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — antes de la primera petición
    app.state.http_client = httpx.AsyncClient()
    yield
    # SHUTDOWN — al apagar el servidor (Ctrl+C o SIGTERM)
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)
```

**Por qué importa:**
- Recursos costosos (clientes HTTP, pools de DB, modelos ML) se crean una vez,
  no por petición.
- El shutdown está garantizado incluso si hay una excepción — no hay fugas de conexiones.
- `app.state` es el almacén compartido entre peticiones — se accede via
  `request.app.state` dentro de los endpoints.

```python
@app.get("/health")
async def health_check(request: Request):
    client = request.app.state.http_client  # el mismo cliente para todas las peticiones
    return {"status": "ok", "client_active": not client.is_closed}
```

▶ Ejecuta el ejemplo:
  `uv run uvicorn scripts.clase_12.conceptos.01_fastapi_lifespan:app --reload`

---

## 3. Depends() — inyección de dependencias

`Depends()` le dice a FastAPI que ejecute una función antes de llamar al endpoint
e inyecte su resultado como parámetro:

```python
from typing import Annotated
from fastapi import Depends, FastAPI

class CommuteService:
    def calculate_eta(self, origin: str, dest: str) -> int:
        return 42

def get_commute_service() -> CommuteService:
    return CommuteService()

# Annotated combina el tipo y el metadato de inyección en un alias reutilizable
ServiceDep = Annotated[CommuteService, Depends(get_commute_service)]

@app.get("/api/v1/eta")
def get_eta(origin: str, destination: str, service: ServiceDep):
    eta = service.calculate_eta(origin, destination)
    return {"origin": origin, "destination": destination, "eta_minutes": eta}
```

**Beneficios sobre instanciar directamente en el endpoint:**
- La fábrica puede recibir sus propias dependencias (anidado)
- Intercambiable en tests via `dependency_overrides` sin tocar el endpoint
- Si la fábrica usa `yield`, FastAPI gestiona el cleanup automáticamente

**Patrón singleton con `@lru_cache`:**

```python
from functools import lru_cache

@lru_cache
def get_commute_service() -> CommuteService:
    # Solo se ejecuta una vez — las siguientes peticiones reciben la misma instancia
    return CommuteService()
```

**En tests — `dependency_overrides`:**

```python
from unittest.mock import MagicMock

def mock_service():
    svc = MagicMock()
    svc.calculate_eta.return_value = 10
    return svc

app.dependency_overrides[get_commute_service] = mock_service
# Todos los endpoints reciben el mock — sin patchear módulos
```

▶ Ejecuta el ejemplo:
  `uv run uvicorn scripts.clase_12.conceptos.02_depends_pattern:app --reload`

---

## 4. Schemas Pydantic — contratos de entrada y salida

FastAPI usa Pydantic V2 para validar automáticamente el cuerpo de las peticiones:

```python
from pydantic import BaseModel, Field, model_validator

class RoutingRequest(BaseModel):
    origin: str = Field(..., min_length=3)
    destination: str = Field(..., min_length=3)
    transport_mode: str = Field(default="driving", pattern="^(driving|transit|walking)$")

    @model_validator(mode="after")
    def check_different_locations(self) -> "RoutingRequest":
        if self.origin.lower() == self.destination.lower():
            raise ValueError("El origen y destino no pueden ser iguales.")
        return self
```

Si el payload no cumple el contrato, FastAPI devuelve `422 Unprocessable Entity`
con detalle de qué campo falló — sin código adicional.

**Response model — filtrar la salida:**

```python
class RoutingResponse(BaseModel):
    route_id: str
    eta_mins: int
    # Solo estos dos campos se serializan — datos internos no se exponen

@app.post("/route", response_model=RoutingResponse)
def create_route(payload: RoutingRequest):
    # Si llega aquí, payload está 100% validado
    return RoutingResponse(route_id="R-999", eta_mins=120)
```

**Capas de validación en orden:**
1. `Field(...)` — tipo, longitud, patrón, rango numérico
2. `model_validator` — lógica cruzada entre campos
3. `response_model` — filtrado de campos en la salida

▶ Ejecuta el ejemplo:
  `uv run uvicorn scripts.clase_12.conceptos.03_pydantic_schemas:app --reload`

---

## 5. Concurrencia estructurada en endpoints

`async def` en un endpoint FastAPI permite usar `await` dentro, pero las
operaciones siguen siendo secuenciales a menos que uses concurrencia explícita.

`anyio.create_task_group()` permite ejecutar varias corutinas en paralelo
dentro de un endpoint:

```python
import anyio

async def fetch_weather(city: str, results: dict):
    await anyio.sleep(1.0)  # simula I/O de red
    results["weather"] = f"Soleado en {city}"

async def fetch_route(origin: str, dest: str, results: dict):
    await anyio.sleep(2.0)  # simula I/O de red
    results["route"] = f"Ruta optima de {origin} a {dest}"

@app.get("/dashboard")
async def get_dashboard(origin: str = "Valencia", dest: str = "Madrid"):
    results = {}

    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch_weather, origin, results)
        tg.start_soon(fetch_route, origin, dest, results)

    # Aqui ambas tareas han terminado — total ~2s, no 3s
    return {"data": results}
```

**Garantías de concurrencia estructurada:**
- Si una tarea lanza excepción, la otra se cancela automáticamente
- No hay tareas huérfanas — el grupo limpia al salir del bloque
- El dict compartido es seguro porque anyio es single-threaded (no hay
  condiciones de carrera en CPython)

Aplicar cuando el endpoint necesita varias fuentes de datos independientes:
weather + route, precio + disponibilidad, etc.

▶ Ejecuta el ejemplo:
  `uv run uvicorn scripts.clase_12.conceptos.04_async_endpoints:app --reload`

---

## 6. Testing con TestClient

`TestClient` ejecuta el servidor en memoria — no hace falta arrancarlo:

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

`TestClient` es sincrono aunque los endpoints sean `async`.

**Combinado con `dependency_overrides`:**

```python
app.dependency_overrides[get_commute_service] = lambda: mock_service
client = TestClient(app)
# Los tests no hacen llamadas reales a servicios externos
```

Ventaja frente a pruebas con `requests` contra un servidor real:
- Sin puerto, sin proceso externo, sin estado entre tests
- Más rápido y determinista
- Los overrides se aplican por test — sin efectos colaterales

▶ Referencia: `scripts/clase_12/ejercicios_clase_12.py` — Ejercicio 4
