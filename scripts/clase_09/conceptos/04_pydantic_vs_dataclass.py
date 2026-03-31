"""Concepto 04 — Pydantic vs dataclass vs TypedDict: cuando usar cada uno.

Los tres tienen su lugar. La eleccion correcta depende del contexto.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_09/conceptos/04_pydantic_vs_dataclass.py

    # Linux
    uv run scripts/clase_09/conceptos/04_pydantic_vs_dataclass.py
"""

import json
from dataclasses import asdict, dataclass
from typing import TypedDict

from pydantic import BaseModel, ValidationError, field_validator


# --- Mismo modelo con los tres enfoques ---

@dataclass
class TemperaturaDataclass:
    ciudad: str
    valor: float


class TemperaturaTypedDict(TypedDict):
    ciudad: str
    valor: float


class TemperaturaPydantic(BaseModel):
    ciudad: str
    valor: float

    @field_validator("valor")
    @classmethod
    def temperatura_valida(cls, v: float) -> float:
        if not -80 <= v <= 60:
            raise ValueError(f"Temperatura irrealista: {v}")
        return round(v, 1)


# --- Diferencia clave 1: validacion ---
print("=== 1. Validacion ===")

# dataclass: acepta cualquier cosa
t1 = TemperaturaDataclass(ciudad="Venus", valor=999.0)
print(f"dataclass  — dato invalido sin error: {t1}")

# TypedDict: no valida en runtime (solo hints para type checkers)
t2: TemperaturaTypedDict = {"ciudad": "Venus", "valor": 999.0}
print(f"TypedDict  — dato invalido sin error: {t2}")

# Pydantic: detecta y rechaza
try:
    TemperaturaPydantic(ciudad="Venus", valor=999.0)
except ValidationError as e:
    print(f"Pydantic   — ValidationError: {e.errors()[0]['msg']}")

# --- Diferencia clave 2: coercion ---
print()
print("=== 2. Coercion de tipos ===")
t3 = TemperaturaPydantic(ciudad="Valencia", valor="13.7")  # str -> float
print(f"Pydantic convierte '13.7' (str) -> {t3.valor} ({type(t3.valor).__name__})")

# --- Diferencia clave 3: serializacion ---
print()
print("=== 3. Serializacion ===")
t4 = TemperaturaDataclass(ciudad="Madrid", valor=25.0)
t5 = TemperaturaPydantic(ciudad="Madrid", valor=25.0)

# dataclass necesita asdict() + json.dumps()
dc_json = json.dumps(asdict(t4))
print(f"dataclass -> JSON: {dc_json}")

# Pydantic tiene metodo directo
py_json = t5.model_dump_json()
print(f"Pydantic  -> JSON: {py_json}")

# --- Cuando usar cada uno ---
print()
print("=== Cuando usar cada uno ===")
print()
print("dataclass:")
print("  [SI] Datos internos del programa, sin fronteras externas")
print("  [SI] Performance critica (menos overhead que Pydantic)")
print("  [SI] Estructuras simples sin validacion necesaria")
print()
print("TypedDict:")
print("  [SI] Documentar la forma de dicts existentes")
print("  [SI] Compatibilidad con codigo que ya usa dicts")
print("  [NO] Cuando necesitas validacion en runtime")
print()
print("Pydantic BaseModel:")
print("  [SI] Datos que cruzan fronteras del sistema (APIs, BD, archivos)")
print("  [SI] Cuando necesitas validacion y normalizacion automatica")
print("  [SI] Cuando el modelo se va a serializar a JSON/API")
print()
print("Regla de PyCommute:")
print("  core/ y services/ usan Pydantic — datos que cruzan capas")
print("  Logica interna que no cruza fronteras puede usar dataclass o dict")
