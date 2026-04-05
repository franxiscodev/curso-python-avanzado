"""Pydantic-Settings: fail-fast con coerción de tipos.

Demuestra lo que ocurre cuando un servidor arranca sin configuración completa:

- PUERTO y MODO_MANTENIMIENTO están en el entorno como strings
- API_KEY_SECRETA NO está en el entorno — campo requerido sin default

Al instanciar AppConfig(), pydantic-settings:
1. Lee PUERTO="8080" y lo convierte a int(8080) automáticamente
2. Lee MODO_MANTENIMIENTO="True" y lo convierte a bool(True)
3. Busca API_KEY_SECRETA y no la encuentra → ValidationError inmediato

El servidor no arranca. El operador ve el error en el momento correcto:
en el inicio, antes de procesar ninguna petición real.

Ejecutar (desde curso/):
    uv run python scripts/clase_03/conceptos/03_pydantic_settings.py
"""

import os
from pydantic_settings import BaseSettings

# Entorno de servidor con configuración incompleta — falta una key requerida
os.environ["PUERTO"] = "8080"
os.environ["MODO_MANTENIMIENTO"] = "True"
# API_KEY_SECRETA no está en el entorno — el campo requerido quedará sin valor


class AppConfig(BaseSettings):
    puerto: int             # Coerción: Convertirá "8080" a entero
    modo_mantenimiento: bool  # Coerción: Convertirá "True" a booleano True
    api_key_secreta: str    # Requerido: No tiene valor por defecto


try:
    # El simple hecho de instanciar la clase dispara la validación
    print("Iniciando servidor...")
    config = AppConfig()  # type: ignore[call-arg]
    print(f"Servidor en puerto: {config.puerto} (Tipo: {type(config.puerto)})")

except Exception as e:
    print("\n[FAIL-FAST ACTIVO] El servidor no puede arrancar:")
    print(e)
