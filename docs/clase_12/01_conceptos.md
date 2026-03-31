# Clase 12 — API REST Profesional con FastAPI

## ¿Qué es una API REST?

Una API REST (Representational State Transfer) expone funcionalidad
a través de HTTP. Cualquier cliente — web, móvil, otro servicio —
puede consumirla sin conocer el lenguaje en que está escrita.

Los conceptos clave:

- **Endpoint:** URL que responde a un método HTTP (`GET`, `POST`, `PUT`, `DELETE`)
- **Request body:** datos enviados por el cliente (JSON)
- **Response:** datos devueltos por el servidor (JSON)
- **Status code:** número que indica éxito (2xx), error cliente (4xx), error servidor (5xx)

---

## FastAPI — framework ASGI

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

---

## APIRouter — organizar endpoints

En lugar de definir todos los endpoints en un solo archivo,
`APIRouter` permite dividirlos por dominio:

```python
# routers/productos.py
from fastapi import APIRouter

router = APIRouter(prefix="/productos")

@router.get("/")           # → GET /productos/
def listar():
    return [{"id": 1, "nombre": "Widget"}]

@router.get("/{id}")       # → GET /productos/42
def obtener(id: int):
    return {"id": id, "nombre": "Widget"}
```

```python
# main.py
from fastapi import FastAPI
from routers import productos

app = FastAPI()
app.include_router(productos.router, tags=["productos"])
```

Los `tags` agrupan endpoints en la documentación automática.

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_12/conceptos/01_fastapi_basico.py`

---

## Depends() — inyección de dependencias

`Depends()` le dice a FastAPI que ejecute una función antes de llamar
al endpoint, e inyecte su resultado como parámetro:

```python
from fastapi import Depends

def get_base_datos():
    return {"conexion": "activa"}   # en real: conexión DB

@app.get("/items")
def listar(db = Depends(get_base_datos)):
    # db ya está resuelto por FastAPI
    return db
```

**FastAPI resuelve el grafo completo:**

```python
def get_config():
    return {"api_key": "abc123"}

def get_cliente(cfg = Depends(get_config)):   # anidado
    return ClienteExterno(cfg["api_key"])

@app.get("/datos")
def obtener(cliente = Depends(get_cliente)):  # FastAPI resuelve la cadena
    return cliente.fetch()
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_12/conceptos/02_depends_pattern.py`

---

## lru_cache con Depends — patrón singleton

Sin cache, `Depends()` crea una nueva instancia en cada request.
Con `@lru_cache`, la primera llamada crea la instancia y las siguientes
devuelven la misma:

```python
from functools import lru_cache

@lru_cache
def get_servicio() -> ServicioPesado:
    print("Creando servicio...")  # solo se ejecuta una vez
    return ServicioPesado()

@app.get("/items")
def listar(svc = Depends(get_servicio)):
    return svc.procesar()
```

**En tests — `dependency_overrides`:**

```python
from unittest.mock import MagicMock

def mock_servicio():
    svc = MagicMock()
    svc.procesar.return_value = [{"id": 1}]
    return svc

app.dependency_overrides[get_servicio] = mock_servicio
# Ahora todos los endpoints reciben el mock — sin patchear módulos
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_12/conceptos/02_depends_pattern.py`

---

## Pydantic en FastAPI — validación automática

FastAPI usa Pydantic para validar request bodies y serializar responses.

**Request body:**

```python
from pydantic import BaseModel, Field

class ProductoIn(BaseModel):
    nombre: str = Field(min_length=1, examples=["Widget Pro"])
    precio: float = Field(gt=0, examples=[9.99])
    activo: bool = Field(default=True)

@app.post("/productos")
def crear(producto: ProductoIn):
    # producto ya está validado — si falla, FastAPI devuelve 422
    return {"id": 1, **producto.model_dump()}
```

**Response model — filtrar campos internos:**

```python
class ProductoOut(BaseModel):
    id: int
    nombre: str
    precio: float
    # 'activo' no aparece — filtrado por response_model

@app.get("/productos/{id}", response_model=ProductoOut)
def obtener(id: int) -> ProductoOut:
    return {"id": id, "nombre": "Widget", "precio": 9.99, "activo": False}
    # FastAPI filtra 'activo' automaticamente
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_12/conceptos/03_pydantic_schemas.py`

---

## Lifespan — startup y shutdown

El lifespan permite ejecutar código al arrancar y al cerrar el servidor:

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup: inicializar recursos costosos
    print("Servidor iniciando...")
    yield
    # shutdown: liberar recursos
    print("Servidor cerrando...")

app = FastAPI(lifespan=lifespan)
```

Usos comunes:
- Conectar a base de datos al arrancar, cerrar conexión al parar
- Cargar modelos ML en RAM al arrancar
- Flush de logs pendientes al cerrar

---

## OpenAPI automático — /docs gratis

FastAPI genera documentación interactiva a partir del código:

```python
@app.post(
    "/productos",
    response_model=ProductoOut,
    summary="Crear un producto",
    description="Crea un nuevo producto en el catálogo.",
)
def crear(producto: ProductoIn) -> ProductoOut:
    ...
```

Accesible en:

- **`/docs`** — Swagger UI interactivo (ejecutar requests desde el browser)
- **`/redoc`** — ReDoc (más legible, menos interactivo)
- **`/openapi.json`** — schema JSON para generar clientes automáticamente

No hay que escribir documentación manualmente — sale del código.

---

## Testing con TestClient

`TestClient` ejecuta el servidor en memoria — no hace falta arrancarlo:

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_crear_producto():
    response = client.post("/productos", json={
        "nombre": "Widget Pro",
        "precio": 9.99,
    })
    assert response.status_code == 200
    assert response.json()["nombre"] == "Widget Pro"
```

`TestClient` es sincrono aunque los endpoints sean `async`.

**Combinado con `dependency_overrides`:**

```python
app.dependency_overrides[get_servicio] = lambda: mock_servicio
client = TestClient(app)
# Los tests no hacen llamadas reales a servicios externos
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_12/conceptos/04_async_endpoints.py`
