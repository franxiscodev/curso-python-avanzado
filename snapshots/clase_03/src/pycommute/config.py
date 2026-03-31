"""Configuración del proyecto validada con Pydantic-Settings.

Nota pedagógica: versión Clase 3 — primera versión de config.py.
"""

# [CLASE 3] Nuevo módulo. Pydantic-Settings reemplaza load_dotenv() + os.getenv().
# Antes (Clases 1-2): os.getenv("OPENWEATHER_API_KEY") devolvía None silenciosamente
# si la variable faltaba — el error aparecía más tarde, en algún punto inesperado.
# Ahora: si falta cualquier variable requerida, el arranque falla con ValidationError
# claro y descriptivo — antes de ejecutar nada.

# [CLASE 8 →] El singleton settings = Settings() es una simplificación deliberada.
# En la arquitectura hexagonal se pasará como dependencia inyectada — pero introducir
# DI ahora sería prematuro. El foco de esta clase es entender Pydantic-Settings.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración validada del proyecto.

    Pydantic-Settings lee las variables desde .env automáticamente.
    Si alguna variable requerida falta, la app lanza ValidationError al arrancar
    — antes de hacer nada — en lugar de fallar silenciosamente en runtime.

    Jerarquía de fuentes (mayor a menor prioridad):
        1. Variables de entorno del sistema
        2. Archivo .env
        3. Valores por defecto definidos en esta clase
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # APIs externas
    openweather_api_key: str
    openrouteservice_api_key: str

    # IA (se usan desde Clase 10)
    google_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma2:2b"

    # App
    app_env: str = "development"
    log_level: str = "DEBUG"


# Instancia única — se importa desde cualquier módulo.
# Se instancia al importar: si la configuración es inválida,
# la app falla aquí — no en medio de una ejecución.
settings = Settings()
