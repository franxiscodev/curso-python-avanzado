"""Dependencias inyectables de FastAPI.

Cada get_*() es una factory cacheada con lru_cache —
el servicio se crea una sola vez y se reutiliza entre requests.
En tests se sobreescribe con app.dependency_overrides.

# [CLASE 12] La factory get_commute_service() es la pieza que conecta
# FastAPI con la arquitectura hexagonal. Construye el CommuteService
# con todos sus adaptadores — FallbackAI, Weather, Route, Cache.
# lru_cache lo convierte en singleton: una instancia por proceso.
# get_settings() como dependencia separada permite reemplazarla en tests
# sin necesitar .env en el directorio de trabajo.
# [CLASE 13 ->] En Docker Compose, settings viene de variables de entorno
#               del container — el codigo no cambia, solo el contexto.
"""

from functools import lru_cache

from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.adapters.fallback_ai import FallbackAIAdapter
from pycommute.adapters.gemini import GeminiAdapter
from pycommute.adapters.ollama_adapter import OllamaAdapter
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.services.commute import CommuteService


def get_settings():
    """Dependencia que expone Settings — sobreescribible en tests.

    Importar settings aqui (no a nivel de modulo) evita ValidationError
    en tests donde no hay .env en el directorio de trabajo.
    """
    from pycommute.config import settings

    return settings


@lru_cache
def get_commute_service() -> CommuteService:
    """Factory cacheada del CommuteService con todos sus adaptadores.

    lru_cache garantiza que se crea una sola instancia por proceso —
    patron singleton sin estado global explicito.
    settings se importa aqui (no a nivel de modulo) para evitar
    ValidationError en tests donde no hay .env en el directorio de trabajo.

    Returns:
        CommuteService listo para recibir requests.
    """
    settings = get_settings()
    ai_adapter = FallbackAIAdapter(
        primary=GeminiAdapter(
            api_key=settings.google_api_key,
            model=settings.gemini_model,
        ),
        secondary=OllamaAdapter(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
        ),
    )
    return CommuteService(
        weather=OpenWeatherAdapter(),
        route=OpenRouteAdapter(),
        cache=MemoryCacheAdapter(),
        ai=ai_adapter,
    )
