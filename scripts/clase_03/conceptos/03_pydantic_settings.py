"""Demo Pydantic-Settings — Clase 3, Concepto 3.

Pydantic-Settings valida la configuración al arrancar.
Si falta una variable requerida, lanza ValidationError inmediatamente
en lugar de devolver None y fallar más tarde.

Ejecuta este script con:
    uv run scripts/clase_03/conceptos/03_pydantic_settings.py
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "mi-app"
    debug: bool = False
    max_retries: int = 3
    api_key: str  # requerida — sin default


# Simular variable de entorno para la demo
os.environ["API_KEY"] = "demo-key-123"

settings = AppSettings()
print(f"App: {settings.app_name}")
print(f"Debug: {settings.debug}")
print(f"Max retries: {settings.max_retries}")
print(f"API Key: {settings.api_key}")

# Demostrar ValidationError cuando falta una variable requerida
del os.environ["API_KEY"]
try:
    bad_settings = AppSettings()
except Exception as e:
    print(f"\nValidationError (esperado):\n{e}")
