"""
Ejercicios — Clase 09: Contratos de Datos con Pydantic V2
==========================================================
Cinco ejercicios sobre BaseModel, Field, validators y model_validator.

Ejecutar (desde curso/):
    uv run python scripts/clase_09/ejercicios_clase_09.py

Requisito: autocontenido, sin imports de pycommute.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — BaseModel simple con 4 campos y tipos
# Define `LecturaClima` con:
#   - ciudad: str
#   - temperatura: float
#   - humedad: int
#   - descripcion: str
# Pista: sección 1 (BaseModel y coerción de tipos) en 01_conceptos.md


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — Field con constraints
# Define `LecturaClimaValidada` igual que LecturaClima pero con:
#   - temperatura: float con ge=-50 y le=60 (entre -50 y 60 grados)
#   - humedad: int con ge=0 y le=100
#   - descripcion: str con min_length=3
# Pista: sección 1 (Field — constraints declarativos) en 01_conceptos.md


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — @field_validator que normaliza un string
# Define `CiudadNormalizada` con:
#   - nombre: str
#   - pais: str
# Añade un @field_validator("nombre", "pais", mode="before") que:
#   - Aplica .strip() para eliminar espacios
#   - Aplica .title() para capitalizar correctamente
#   - Retorna el valor normalizado
# Ejemplo: CiudadNormalizada(nombre="  valencia  ", pais="ESPAÑA")
#          → nombre="Valencia", pais="España"
# Pista: sección 2 (@field_validator — reglas de negocio por campo) en 01_conceptos.md
class CiudadNormalizada(BaseModel):
    nombre: str
    pais: str

    # TODO: añade el @field_validator aquí
    pass


# ---------------------------------------------------------------------------
# Ejercicio 4
# ---------------------------------------------------------------------------

# TODO: Ejercicio 4 — @model_validator que valida consistencia entre campos
# Define `RangoTemperatura` con:
#   - ciudad: str
#   - temp_min: float
#   - temp_max: float
# Añade un @model_validator(mode="after") que:
#   - Verifica que temp_min <= temp_max
#   - Si no, lanza ValueError("temp_min no puede ser mayor que temp_max")
# Pista: sección 3 (@model_validator — validación entre múltiples campos) en 01_conceptos.md
class RangoTemperatura(BaseModel):
    ciudad: str
    temp_min: float
    temp_max: float

    # TODO: añade el @model_validator aquí
    pass


# ---------------------------------------------------------------------------
# Ejercicio 5
# ---------------------------------------------------------------------------

# TODO: Ejercicio 5 — Modelo con alias y model_config
# Define `EstacionMeteo` con model_config = ConfigDict(populate_by_name=True) y:
#   - station_id: str con alias "id"
#   - station_name: str con alias "name"
#   - elevation_m: float con alias "elevation"
# El modelo debe poder construirse tanto con los nombres Python como con los alias.
# Ejemplo:
#   e1 = EstacionMeteo(id="ES001", name="Valencia", elevation=12.5)
#   e2 = EstacionMeteo(station_id="ES001", station_name="Valencia", elevation_m=12.5)
# Pista: sección 1 (Field con alias — mapeo de nombres externos) en 01_conceptos.md
# from pydantic import ConfigDict  # ya disponible si lo necesitas


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo() -> None:
    from pydantic import ValidationError

    print("=== Ejercicio 1: LecturaClima ===")
    try:
        lectura = LecturaClima(  # type: ignore[name-defined]
            ciudad="Valencia", temperatura=22.5, humedad=65, descripcion="soleado"
        )
        print(f"  {lectura}")
    except NameError:
        print("  Sin implementar aún.")

    print("\n=== Ejercicio 2: LecturaClimaValidada ===")
    try:
        ok = LecturaClimaValidada(  # type: ignore[name-defined]
            ciudad="Madrid", temperatura=25.0, humedad=50, descripcion="nublado"
        )
        print(f"  Válida: {ok}")
        try:
            LecturaClimaValidada(  # type: ignore[name-defined]
                ciudad="Madrid", temperatura=100.0, humedad=50, descripcion="nublado"
            )
        except ValidationError as e:
            print(f"  Error esperado (temp=100): {e.errors()[0]['msg']}")
    except NameError:
        print("  Sin implementar aún.")

    print("\n=== Ejercicio 3: CiudadNormalizada ===")
    try:
        ciudad = CiudadNormalizada(nombre="  valencia  ", pais="ESPAÑA")
        print(f"  nombre='{ciudad.nombre}', pais='{ciudad.pais}'")
    except Exception as e:
        print(f"  Sin implementar aún: {e}")

    print("\n=== Ejercicio 4: RangoTemperatura ===")
    try:
        rango_ok = RangoTemperatura(ciudad="Valencia", temp_min=10.0, temp_max=35.0)
        print(f"  Rango válido: {rango_ok.temp_min} - {rango_ok.temp_max}")
        try:
            RangoTemperatura(ciudad="Valencia", temp_min=40.0, temp_max=20.0)
        except ValidationError as e:
            print(f"  Error esperado: {e.errors()[0]['msg']}")
    except Exception as e:
        print(f"  Sin implementar aún: {e}")

    print("\n=== Ejercicio 5: EstacionMeteo ===")
    try:
        e1 = EstacionMeteo(id="ES001", name="Valencia Norte", elevation=12.5)  # type: ignore[name-defined]
        e2 = EstacionMeteo(station_id="ES002", station_name="Madrid Sur", elevation_m=650.0)  # type: ignore[name-defined]
        print(f"  Por alias:  id={e1.station_id}, name={e1.station_name}")
        print(f"  Por nombre: id={e2.station_id}, name={e2.station_name}")
    except (NameError, Exception) as e:
        print(f"  Sin implementar aún: {e}")


if __name__ == "__main__":
    demo()
