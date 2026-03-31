"""Schemas Pydantic en FastAPI — request validation y OpenAPI.

Demuestra:
- Diferencia entre modelos de dominio y schemas HTTP (DTO pattern)
- Validacion automatica de request body
- Schema OpenAPI generado por Pydantic (lo que aparece en /docs)
- Como Field(examples=...) mejora la documentacion interactiva

No ejecuta FastAPI — solo muestra validacion y schemas.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_12/conceptos/03_pydantic_schemas.py

    # Linux
    uv run scripts/clase_12/conceptos/03_pydantic_schemas.py
"""

import json

from pydantic import BaseModel, Field


# ── Ejemplo de DTO pattern: dominio vs HTTP ───────────────────────────

class ViajeInterno(BaseModel):
    """Modelo de dominio — representa el concepto en el sistema."""
    ciudad_origen: str
    ciudad_destino: str
    distancia_km: float
    duracion_min: float
    temperatura_origen: float


class ViajeRequest(BaseModel):
    """Schema HTTP de request — lo que el cliente envia."""
    origen: str = Field(min_length=1, examples=["Valencia"])
    destino: str = Field(min_length=1, examples=["Madrid"])
    perfiles: list[str] = Field(
        default=["driving-car"],
        examples=[["driving-car", "cycling-regular"]],
    )
    incluir_ia: bool = Field(default=True, description="Generar recomendacion de IA")


class ViajeResponse(BaseModel):
    """Schema HTTP de response — lo que la API devuelve al cliente."""
    origen: str
    destino: str
    distancia_km: float
    duracion_min: float
    recomendacion: str | None = None


# ── Validacion de request ─────────────────────────────────────────────
print("=== Validacion de request ===")

try:
    req = ViajeRequest(origen="Valencia", destino="Madrid")
    print(f"  Valido: {req.model_dump()}")
except Exception as e:
    print(f"  Error: {e}")

try:
    req_invalido = ViajeRequest(origen="", destino="Madrid")
except Exception as e:
    print(f"  Invalido (origen vacio): {type(e).__name__}")

# ── Schema OpenAPI generado ───────────────────────────────────────────
print("\n=== Schema OpenAPI de ViajeRequest ===")
schema = ViajeRequest.model_json_schema()
print(json.dumps(schema, ensure_ascii=False, indent=2))
print("\n→ Este schema aparece automaticamente en /docs de FastAPI")

# ── Por que DTO y no reutilizar el modelo de dominio ─────────────────
print("\n=== Por que separar dominio y HTTP ===")
print("""
  Modelo de dominio (ViajeInterno):
    - Representa el concepto en el sistema
    - Puede tener logica de negocio, validadores, computed fields
    - No deberia depender del formato HTTP

  Schema HTTP (ViajeRequest / ViajeResponse):
    - Define el contrato con los clientes de la API
    - Puede evolucionar independientemente del dominio
    - Tiene Field(examples=...) para documentacion Swagger

  Si manana cambia la estructura de la API (nuevo campo, renombrado),
  solo cambia el schema HTTP — el dominio no se toca.
  Este patron se llama DTO (Data Transfer Object).
""")
