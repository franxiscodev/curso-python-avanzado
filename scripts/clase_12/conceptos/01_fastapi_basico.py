"""FastAPI basico — patron de endpoints, Pydantic y routing.

Muestra el patron completo de una mini API con FastAPI.
No ejecuta el servidor — imprime el codigo y las instrucciones.

Para ejecutarlo como servidor:
    Guardar el bloque de codigo en un archivo app.py y ejecutar:

    # Windows (PowerShell)
    uv run uvicorn app:app --reload --port 8001

    # Linux
    uv run uvicorn app:app --reload --port 8001

    Abrir: http://localhost:8001/docs

Ejecutar este script:
    # Windows (PowerShell)
    uv run scripts/clase_12/conceptos/01_fastapi_basico.py

    # Linux
    uv run scripts/clase_12/conceptos/01_fastapi_basico.py
"""

from pydantic import BaseModel, Field

# ── Mostrar el patron de una mini API ────────────────────────────────
codigo = '''
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Demo API PyCommute")


class ItemRequest(BaseModel):
    nombre: str = Field(min_length=1, examples=["Valencia"])
    precio: float = Field(gt=0)


class ItemResponse(BaseModel):
    id: int
    nombre: str
    precio: float
    mensaje: str


# GET sin parametros
@app.get("/health")
async def health():
    return {"status": "ok"}

# GET con parametro de ruta
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"id": item_id, "nombre": "ejemplo"}

# GET con query parameter
@app.get("/items")
async def list_items(limit: int = 10, offset: int = 0):
    return {"items": [], "limit": limit, "offset": offset}

# POST con body validado por Pydantic
@app.post("/items", response_model=ItemResponse)
async def crear_item(item: ItemRequest) -> ItemResponse:
    return ItemResponse(
        id=1,
        nombre=item.nombre,
        precio=item.precio,
        mensaje=f"Item \'{item.nombre}\' creado exitosamente",
    )
'''

print("=== Patron FastAPI basico ===")
print(codigo)
print("Ejecutar con:")
print("  uv run uvicorn <archivo>:app --reload --port 8001")
print("  Abrir: http://localhost:8001/docs")

# ── Demostrar validacion Pydantic sin servidor ────────────────────────
print("\n=== Validacion Pydantic (sin servidor) ===")


class ItemRequest(BaseModel):
    nombre: str = Field(min_length=1, examples=["Valencia"])
    precio: float = Field(gt=0)


try:
    item = ItemRequest(nombre="Valencia", precio=99.9)
    print(f"  Valido: nombre={item.nombre}, precio={item.precio}")
except Exception as e:
    print(f"  Error: {e}")

try:
    item_invalido = ItemRequest(nombre="", precio=-1)
except Exception as e:
    print(f"  Invalido: {type(e).__name__} — {str(e)[:80]}")
