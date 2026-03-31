"""Concepto 02 — @field_validator: logica de validacion custom.

Cuando los constraints de Field (gt, min_length) no son suficientes,
@field_validator permite escribir logica arbitraria de validacion.
Siempre requiere @classmethod en Pydantic V2.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_09/conceptos/02_field_validators.py

    # Linux
    uv run scripts/clase_09/conceptos/02_field_validators.py
"""

from pydantic import BaseModel, Field, ValidationError, field_validator


class Temperatura(BaseModel):
    ciudad: str
    valor: float
    unidad: str = Field(default="celsius")

    @field_validator("ciudad")
    @classmethod
    def ciudad_capitalizada(cls, v: str) -> str:
        """Normaliza el nombre de la ciudad — siempre Title Case."""
        return v.strip().title()

    @field_validator("valor")
    @classmethod
    def temperatura_realista(cls, v: float) -> float:
        """Valida rango realista para temperatura terrestre."""
        if not -89.2 <= v <= 56.7:  # records historicos reales
            raise ValueError(
                f"{v}C esta fuera del rango historico terrestre "
                f"(-89.2C a 56.7C)"
            )
        return round(v, 1)

    @field_validator("unidad")
    @classmethod
    def unidad_valida(cls, v: str) -> str:
        validas = {"celsius", "fahrenheit", "kelvin"}
        v_lower = v.lower()
        if v_lower not in validas:
            raise ValueError(f"Unidad '{v}' no valida. Usar: {validas}")
        return v_lower


# --- Normalizacion en accion ---
print("=== Normalizacion automatica ===")
casos = [
    ("  valencia  ", 13.5, "Celsius"),    # espacios + mayusc unidad
    ("MADRID", 25.0, "celsius"),           # ciudad en mayusculas
    ("buenos aires", -10.0, "CELSIUS"),    # ciudad minusc + unidad mayusc
]
for ciudad, temp, unidad in casos:
    t = Temperatura(ciudad=ciudad, valor=temp, unidad=unidad)
    print(f"  '{ciudad}' -> '{t.ciudad}' | {temp} -> {t.valor} | '{unidad}' -> '{t.unidad}'")

# --- Fallo esperado ---
print()
print("=== Temperatura fuera de rango (Venus: 462C) ===")
try:
    Temperatura(ciudad="Venus", valor=462.0, unidad="celsius")
except ValidationError as e:
    for error in e.errors():
        print(f"  ValidationError en '{error['loc'][0]}': {error['msg']}")

# --- Diferencia mode before vs after ---
print()
print("=== mode='before' vs mode='after' ===")
print("  mode='after'  (default): recibe el valor YA parseado por Pydantic")
print("  mode='before': recibe el valor RAW antes del parseo")
print()
print("  Ejemplo: si campo es float y llega '13.5' (str):")
print("    mode='after'  -> recibe 13.5 (float) — Pydantic ya convirtio")
print("    mode='before' -> recibe '13.5' (str) — antes de la conversion")
