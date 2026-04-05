"""Pydantic V2 — @model_validator: validación entre múltiples campos.

Demuestra cómo validar invariantes que involucran la relación entre
dos o más campos del modelo. @field_validator solo ve un campo a la vez;
@model_validator tiene acceso a todos los campos ya validados.

mode="after" significa que se ejecuta después de que Pydantic haya
validado y convertido cada campo individualmente.

Conceptos que ilustra:
- @model_validator(mode="after") — recibe self con todos los campos listos
- Invariante del modelo: la relación fin > inicio siempre se garantiza
- Orden de ejecución: field_validators primero, model_validator al final
- Si un field_validator falla, el model_validator no se ejecuta

Ejecutar:
    uv run python scripts/clase_09/conceptos/03_model_validator.py
"""

from loguru import logger
from pydantic import BaseModel, ValidationError, model_validator

logger.info("--- @model_validator: invariante entre campos ---")


class RangoFechas(BaseModel):
    # Fechas en formato AAAAMMDD como entero (simplificado para evitar imports de datetime).
    # La regla de negocio: fin debe ser posterior a inicio. Ningún field_validator
    # puede verificar esto porque cada uno solo ve su propio campo.
    inicio: int
    fin: int

    # mode="after": se ejecuta después de que Pydantic validó inicio y fin por separado.
    # self ya tiene los valores convertidos a int — es seguro compararlos.
    @model_validator(mode="after")
    def verificar_rango_logico(self) -> "RangoFechas":
        print(f"  Validando rango: inicio={self.inicio}, fin={self.fin}")

        if self.fin <= self.inicio:
            # Esta es la única forma de validar una relación entre campos:
            # el model_validator tiene visión completa del objeto.
            raise ValueError(
                "La fecha 'fin' debe ser estrictamente posterior a la fecha 'inicio'"
            )

        # Siempre devolver self — permite modificar campos derivados si fuera necesario.
        return self


# CASO A: Rango con sentido cronológico — el model_validator lo deja pasar
try:
    r1 = RangoFechas(inicio=20240101, fin=20241231)
    logger.success(f"Rango valido creado: {r1}")
except ValidationError as e:
    logger.error(e)

# CASO B: Fin anterior a inicio — la regla cross-field detecta la incoherencia
print("\n--- Intento con rango invertido ---")
try:
    RangoFechas(inicio=20241231, fin=20240101)  # fin < inicio → inválido
except ValidationError as e:
    print(f"\n--- ValidationError ---\n{e}")
