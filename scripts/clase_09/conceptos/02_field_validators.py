"""Pydantic V2 — @field_validator: reglas de negocio por campo.

Demuestra cómo ir más allá de los constraints declarativos de Field()
cuando la regla de negocio no se puede expresar con ge/le/pattern.

@field_validator recibe el valor ya convertido al tipo declarado (modo "after"
por defecto) y puede validarlo, rechazarlo o transformarlo.

Conceptos que ilustra:
- @field_validator + @classmethod (obligatorio en Pydantic V2)
- Levantar ValueError dentro del validador → Pydantic lo envuelve en ValidationError
- El validador puede transformar el valor: recibe v, retorna v modificado
- Dos casos: dato lógico (pasa) y dato físicamente imposible (falla)

Ejecutar:
    uv run python scripts/clase_09/conceptos/02_field_validators.py
"""

from loguru import logger
from pydantic import BaseModel, ValidationError, field_validator

logger.info("--- @field_validator: regla de negocio por campo ---")


class SensorTemperatura(BaseModel):
    id: int
    # La lectura en grados Celsius no puede bajar del cero absoluto (-273.15 C).
    # Esta regla no se puede expresar con Field(ge=...) porque -273.15 no es 0.
    lectura: float

    # @classmethod es OBLIGATORIO en Pydantic V2 (en V1 era opcional).
    # Sin él, Pydantic V2 lanza un TypeError confuso al definir la clase.
    @field_validator("lectura")
    @classmethod
    def validar_cero_absoluto(cls, v: float) -> float:
        # 'v' es el valor ya convertido a float por Pydantic (modo "after").
        # En este punto es seguro comparar con -273.15.
        print(f"  Validando lectura: {v}")
        if v < -273.15:
            # ValueError dentro del validador → Pydantic lo convierte en ValidationError.
            raise ValueError(
                "La temperatura no puede ser inferior al cero absoluto (-273.15 C)"
            )
        # Siempre devolver el valor (aquí podríamos transformarlo: round(v, 2), etc.)
        return v


# CASO A: Lectura física válida — el validador la deja pasar
try:
    s1 = SensorTemperatura(id=1, lectura=25.5)
    logger.success(f"Sensor valido creado: {s1}")
except ValidationError as e:
    logger.error(e)

# CASO B: Lectura físicamente imposible — el validador la rechaza
print("\n--- Intento con valor por debajo del cero absoluto ---")
try:
    SensorTemperatura(id=2, lectura=-300.0)  # -300 < -273.15 → inválido
except ValidationError as e:
    # El ValidationError incluye: campo ("lectura"), valor (-300.0) y mensaje del ValueError.
    print(f"\n--- ValidationError ---\n{e}")
