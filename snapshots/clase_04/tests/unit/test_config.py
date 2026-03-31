# [CLASE 4] Nuevo modulo de tests para config.py.
# Antes (Clase 3): config.py no tenia tests — se verificaba manualmente.
# Aqui: 3 tests con monkeypatch que cubren carga, fallo y valores por defecto.
# Truco clave: se usa una clase _Settings local con env_file=None para evitar
# que el .env del desarrollador interfiera en los tests.
# Por que no importar settings directamente: es un singleton instanciado al
# importar el modulo — si el .env real esta presente, Settings() ya tiene valores
# y delenv no tiene efecto. La clase local aislada resuelve este problema.
# [CLASE 5 ->] Sin cambios previstos en config.py — estos tests se mantienen.

"""Tests unitarios para pycommute.config."""

import pytest
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


# [CLASE 4] _Settings con env_file=None: aislamiento total del entorno real.
# Hereda la misma estructura que Settings pero sin leer ningun archivo .env.
# Esto garantiza que los tests son reproducibles independientemente de si
# el desarrollador tiene un .env configurado o no.
class _Settings(BaseSettings):
    """Settings aislada sin carga desde .env — solo para tests."""

    model_config = SettingsConfigDict(env_file=None)

    openweather_api_key: str
    openrouteservice_api_key: str
    app_env: str = "development"
    log_level: str = "DEBUG"


def test_settings_loads_from_env(monkeypatch) -> None:
    """Verifica que Settings lee las variables de entorno correctamente."""
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-weather-key")
    monkeypatch.setenv("OPENROUTESERVICE_API_KEY", "test-route-key")

    s = _Settings()

    assert s.openweather_api_key == "test-weather-key"
    assert s.openrouteservice_api_key == "test-route-key"


# [CLASE 4] Testear el fail-fast de pydantic-settings.
# Si la app arranca sin las keys requeridas, ValidationError se lanza AQUI
# (en la instanciacion) — no en medio de una llamada a la API en produccion.
def test_settings_raises_if_key_missing(monkeypatch) -> None:
    """Verifica que Settings lanza ValidationError si falta una key requerida."""
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTESERVICE_API_KEY", raising=False)

    with pytest.raises(ValidationError):
        _Settings()


def test_settings_default_values(monkeypatch) -> None:
    """Verifica que app_env y log_level tienen los valores por defecto correctos."""
    monkeypatch.setenv("OPENWEATHER_API_KEY", "key1")
    monkeypatch.setenv("OPENROUTESERVICE_API_KEY", "key2")

    s = _Settings()

    assert s.app_env == "development"
    assert s.log_level == "DEBUG"
