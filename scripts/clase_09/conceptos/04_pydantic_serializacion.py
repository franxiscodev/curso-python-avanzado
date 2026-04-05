"""Pydantic V2 — Serialización: model_dump, aliases y exclusiones.

Demuestra cómo exportar datos de un modelo Pydantic con control total
sobre qué sale y con qué nombres. Tres escenarios habituales:
- Dump estándar a dict Python (para ORMs, librerías internas)
- Dump con alias para una API externa que espera nombres distintos
- Dump directo a JSON string con exclusiones dinámicas

Conceptos que ilustra:
- model_dump() → dict con los nombres Python del modelo
- Field(serialization_alias=...) → nombre alternativo en la salida
- model_dump(by_alias=True) → activa los serialization_alias
- Field(exclude=True) → campo que nunca aparece en el dump (ej: tokens)
- model_dump_json(...) → string JSON directo, más rápido que json.dumps

Ejecutar:
    uv run python scripts/clase_09/conceptos/04_pydantic_serializacion.py
"""

from loguru import logger
from pydantic import BaseModel, Field

logger.info("--- Serializacion con model_dump ---")


class UsuarioAPI(BaseModel):
    id: int
    username: str
    # serialization_alias: nombre que usará la API externa en el JSON de respuesta.
    # El campo se llama "email" en Python pero sale como "user_email" al serializar.
    email: str = Field(..., serialization_alias="user_email")
    # exclude=True: este campo existe en el objeto Python pero NUNCA sale en ningún dump.
    # Perfecto para datos sensibles que no deben llegar al cliente (tokens, passwords).
    token_interno: str = Field(exclude=True)


# El objeto se crea con los nombres Python normales — token_interno incluido.
usuario = UsuarioAPI(
    id=1, username="nandodev", email="nando@example.com", token_interno="secret_xyz_123"
)

logger.info(f"Objeto Pydantic en memoria: {usuario}")

# --- ESCENARIO A: Dump estándar a dict Python ---
# Usa los nombres Python del modelo (no los alias).
# token_interno ya está excluido por Field(exclude=True).
print("\n--- model_dump() estandar ---")
dump_std = usuario.model_dump()
print(dump_std)
assert "token_interno" not in dump_std  # nunca aparece, aunque existe en el objeto
assert "email" in dump_std             # nombre Python, no el alias


# --- ESCENARIO B: Dump para API externa con alias ---
# by_alias=True activa los serialization_alias declarados en los campos.
# El campo "email" pasa a llamarse "user_email" en el dict resultante.
print("\n--- model_dump(by_alias=True) ---")
dump_api = usuario.model_dump(by_alias=True)
print(dump_api)
assert "user_email" in dump_api   # alias activo
assert "email" not in dump_api    # nombre Python sustituido por el alias

# --- ESCENARIO C: Dump directo a JSON string ---
# model_dump_json es más rápido que json.dumps(model_dump(...)).
# Se pueden añadir exclusiones adicionales ad-hoc en el mismo llamado.
print("\n--- model_dump_json(by_alias=True, exclude={'id'}) ---")
json_api = usuario.model_dump_json(by_alias=True, exclude={"id"})
print(json_api)
# Resultado: {"username":"nandodev","user_email":"nando@example.com"}
