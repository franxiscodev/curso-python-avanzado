"""Concepto 03 — @model_validator: validacion entre campos y valores derivados.

Cuando la validacion requiere ver MULTIPLES campos a la vez,
o calcular un valor a partir de otros, @model_validator(mode='after')
tiene acceso al modelo completo ya construido.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_09/conceptos/03_model_validator.py

    # Linux
    uv run scripts/clase_09/conceptos/03_model_validator.py
"""

from datetime import date

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


class Reserva(BaseModel):
    hotel: str
    fecha_entrada: date
    fecha_salida: date
    huespedes: int = Field(ge=1, le=10)
    noches: int = 0  # se calcula automaticamente

    @field_validator("hotel")
    @classmethod
    def hotel_no_vacio(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def validar_fechas_y_calcular_noches(self) -> "Reserva":
        """Valida que fecha_salida > fecha_entrada y calcula noches.

        mode='after': tiene acceso a todos los campos ya validados.
        Se ejecuta DESPUES de los field_validators.
        """
        if self.fecha_salida <= self.fecha_entrada:
            raise ValueError(
                "fecha_salida debe ser posterior a fecha_entrada"
            )
        self.noches = (self.fecha_salida - self.fecha_entrada).days
        return self


# --- Uso correcto ---
print("=== Reserva valida ===")
reserva = Reserva(
    hotel="Hotel Valencia",
    fecha_entrada=date(2024, 6, 15),
    fecha_salida=date(2024, 6, 18),
    huespedes=2,
)
print(f"Hotel:    {reserva.hotel}")
print(f"Entrada:  {reserva.fecha_entrada}")
print(f"Salida:   {reserva.fecha_salida}")
print(f"Noches:   {reserva.noches}  <- calculado automaticamente")
print(f"Dict:     {reserva.model_dump()}")

# --- Fallo: fechas invertidas ---
print()
print("=== Fechas invertidas (error) ===")
try:
    Reserva(
        hotel="Hotel Test",
        fecha_entrada=date(2024, 6, 18),
        fecha_salida=date(2024, 6, 15),
        huespedes=1,
    )
except ValidationError as e:
    for error in e.errors():
        print(f"  ValidationError: {error['msg']}")

# --- Analogia con CommuteResult ---
print()
print("=== Mismo patron en PyCommute ===")
print("CommuteResult.set_best_route() es un model_validator(mode='after'):")
print("  - recibe routes ya validados como list[RouteData]")
print("  - calcula best_route = min(routes, key=lambda r: r.duration_min)")
print("  - el llamador no necesita calcularlo — siempre esta disponible")
