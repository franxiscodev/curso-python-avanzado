"""Pydantic V2 — Coerción de tipos y ValidationError.

Demuestra que Pydantic no solo verifica tipos sino que los convierte
(coerción): recibe un dato "sucio" de una fuente externa (JSON, CSV,
form HTTP) y lo transforma al tipo declarado en el modelo.

Cuando la conversión no es posible, lanza ValidationError con el
mensaje exacto del campo que falló.

Conceptos que ilustra:
- BaseModel como contrato de datos: los type hints son reglas, no sugerencias
- Coerción automática (lax mode): "101" -> int, "true" -> bool
- ValidationError: qué pasa cuando el dato no se puede convertir
- Dos casos contrastados: dato coercible vs dato incoercible

Ejecutar:
    uv run python scripts/clase_09/conceptos/01_pydantic_coercion.py
"""

from loguru import logger
from pydantic import BaseModel, ValidationError


# 1. Definición del Contrato Inmutable
class Dispositivo(BaseModel):
    # Definimos que estos campos SON int y bool
    id: int
    esta_activo: bool


logger.info("--- COERCION DE TIPOS CON PYDANTIC ---")

# CASO A: Datos "sucios" procedentes de JSON (todo llega como string)
# Las APIs y archivos CSV representan todo como texto.
# Sin Pydantic habría que convertir manualmente: int(datos["id"]), etc.
datos_entrada = {
    "id": "101",       # string en el JSON, int en el modelo
    "esta_activo": "true",  # string en el JSON, bool en el modelo
}

try:
    # Pydantic convierte los strings al tipo declarado en el modelo.
    # El __init__ generado por BaseModel hace la coerción implícitamente.
    dispositivo = Dispositivo(**datos_entrada)

    print(f"Objeto creado: {dispositivo}")
    print(f"Tipo de id: {type(dispositivo.id)}")           # <class 'int'>
    print(f"Tipo de esta_activo: {type(dispositivo.esta_activo)}")  # <class 'bool'>

    # Los campos son los tipos correctos, aunque los inputs eran strings
    assert dispositivo.id == 101
    assert dispositivo.esta_activo is True
    logger.success("Coercion exitosa: String '101' -> Int 101, 'true' -> True")

except ValidationError as e:
    logger.error(f"Error inesperado: {e}")

# CASO B: Dato que Pydantic no puede convertir a ningún tipo razonable.
# "no_soy_un_numero" no tiene conversión válida a int → ValidationError.
# El error incluye: qué campo falló, qué valor llegó, por qué falló.
datos_basura = {"id": "no_soy_un_numero", "esta_activo": "tal vez"}
try:
    Dispositivo(**datos_basura)
except ValidationError as e:
    # ValidationError agrega todos los errores del objeto, no solo el primero.
    print(f"\n--- ValidationError (todos los errores del objeto) ---\n{e}")
