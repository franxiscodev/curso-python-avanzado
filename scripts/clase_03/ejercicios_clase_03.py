"""
Ejercicios — Clase 03: Resiliencia Profesional
===============================================
Tres ejercicios sobre loguru, pydantic-settings y tenacity.

Ejecutar (desde curso/):
    uv run python scripts/clase_03/ejercicios_clase_03.py

Requisito: autocontenido, sin imports de pycommute.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic_settings import BaseSettings
from tenacity import retry, stop_after_attempt, wait_fixed, before_log, after_log


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Configurar loguru con sink a archivo y formato personalizado
# Implementa `configurar_logger` que:
#   1. Elimina el handler por defecto de loguru (logger.remove())
#   2. Añade un handler a sys.stdout con nivel "DEBUG" y formato:
#      "{time:HH:mm:ss} | {level:<8} | {message}"
#   3. Añade un handler a un archivo "app.log" con nivel "WARNING"
#   4. Retorna None
# Después de llamar a la función, loguea una línea INFO y una WARNING para probar.
# Pista: repasa "Configuración avanzada con logger.add()" en 01_conceptos.md
def configurar_logger() -> None:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — Clase Settings con pydantic-settings
# Define una clase `AppSettings` que herede de `BaseSettings` con:
#   - app_name: str con valor default "PyCommute"
#   - debug: bool con valor default False
#   - max_retries: int con valor default 3
#   - api_url: str con valor default "https://api.example.com"
# Añade model_config = SettingsConfigDict(env_prefix="APP_") para que las
# variables de entorno tengan prefijo APP_ (ej: APP_DEBUG=true).
# Pista: repasa "pydantic-settings — configuración tipada" en 01_conceptos.md
#
# from pydantic_settings import SettingsConfigDict  # ya importado arriba si lo necesitas
class AppSettings(BaseSettings):
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Contador para Ejercicio 3
# ---------------------------------------------------------------------------

_intento_actual: int = 0


def _operacion_inestable() -> str:
    """Simula una operación que falla las primeras 2 veces y luego tiene éxito."""
    global _intento_actual
    _intento_actual += 1
    if _intento_actual < 3:
        raise ConnectionError(f"Fallo simulado en intento {_intento_actual}")
    return "conexión establecida"


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — Función con @retry que falla antes de tener éxito
# Implementa `conectar_con_retry` que:
#   1. Usa el decorador @retry de tenacity con:
#      - stop=stop_after_attempt(5)
#      - wait=wait_fixed(0)   ← 0 segundos para que el test sea rápido
#      - before=before_log(logger, "DEBUG")
#      - after=after_log(logger, "INFO")
#   2. Llama a `_operacion_inestable()` y retorna su resultado
# NOTA: `_intento_actual` ya está inicializado en 0 — no lo modifiques.
# La función debe tener éxito en el intento 3.
# Pista: repasa "Tenacity — reintentos declarativos" en 01_conceptos.md
def conectar_con_retry() -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo() -> None:
    print("=== Ejercicio 1: configurar_logger ===")
    configurar_logger()
    logger.info("Logger configurado correctamente")
    logger.warning("Esta línea también va al archivo app.log")
    logger.debug("Mensaje de debug — solo en consola")

    print("\n=== Ejercicio 2: AppSettings ===")
    settings = AppSettings()
    if hasattr(settings, "app_name"):
        print(f"app_name   = {settings.app_name}")
        print(f"debug      = {settings.debug}")
        print(f"max_retries= {settings.max_retries}")
        print(f"api_url    = {settings.api_url}")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 3: conectar_con_retry ===")
    global _intento_actual
    _intento_actual = 0  # reiniciar para la demo
    resultado = conectar_con_retry()
    if resultado is not None:
        print(f"Resultado: {resultado}")
    else:
        print("Sin implementar aún.")


if __name__ == "__main__":
    demo()
