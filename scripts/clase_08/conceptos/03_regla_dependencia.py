"""
Concepto 3: La regla de dependencia — el Core no conoce el exterior.

El script está dividido en tres capas explícitas con comentarios [CAPA N]:

  CAPA 1 — Core/Dominio:
    WeatherCondition es el modelo de dominio (Pydantic).
    WeatherPort es el contrato que el Core exige a cualquier proveedor.
    TripAnalyzer contiene lógica de negocio pura: sin httpx, sin URLs,
    sin API keys. Solo trabaja con WeatherCondition y WeatherPort.

  CAPA 2 — Infraestructura/Adaptadores:
    OpenWeatherAdapter implementa WeatherPort traduciendo la respuesta
    real de la API (temperatura en Kelvin, dict anidado) al modelo del
    Core (WeatherCondition con temp_celsius).
    La conversión de Kelvin a Celsius es responsabilidad del adaptador,
    no del Core — el Core no sabe que la API usa Kelvin.

  CAPA 3 — Aplicación (el ensamblador):
    Crea el adaptador, lo inyecta en el Core, ejecuta.
    Es la única capa que conoce ambas partes.

Por qué el Core NO importa httpx:
  Si TripAnalyzer importase httpx, un cambio en httpx o en la URL de
  la API podría romper la lógica de negocio. Al prohibir esa dirección,
  el Core es portable: puede testearse sin red, sin API keys, sin Docker.

Conexión con el proyecto:
  La estructura core/adapters/services/ de PyCommute sigue exactamente
  estas tres capas. core/ports.py es el WeatherPort de este script.

Ejecutar:
  uv run python scripts/clase_08/conceptos/03_regla_dependencia.py
"""

# ==============================================================================
# [CAPA 1: CORE / DOMINIO]
# ¡OJO! Aquí NO hay `import httpx` ni librerías de I/O.
# El Core solo depende de Python puro y herramientas de dominio (Pydantic).
# ==============================================================================
from typing import Protocol

from pydantic import BaseModel, Field


class WeatherCondition(BaseModel):
    """La entidad de dominio. Dicta cómo el Core entiende el clima."""

    temp_celsius: float = Field(..., description="Temperatura en grados Celsius")
    is_raining: bool


class WeatherPort(Protocol):
    """El Core exige este contrato a cualquier proveedor de clima."""

    def fetch_weather(self, city: str) -> WeatherCondition: ...


class TripAnalyzer:
    """Lógica de negocio Pura. Ignora el mundo exterior."""

    def __init__(self, weather_api: WeatherPort):
        self.weather = weather_api

    def should_take_umbrella(self, city: str) -> bool:
        # El Core confía ciegamente en que el adaptador le dará un WeatherCondition válido
        condition = self.weather.fetch_weather(city)

        # Regla de negocio crítica
        return condition.is_raining or condition.temp_celsius < 10.0


# ==============================================================================
# [CAPA 2: INFRAESTRUCTURA / ADAPTADORES]
# Esta capa SÍ importa librerías externas y DEPENDE del Core
# para saber qué estructura (WeatherCondition) debe devolver.
# ==============================================================================


class OpenWeatherAdapter:
    """Implementa WeatherPort traduciendo la API externa al Dominio."""

    def fetch_weather(self, city: str) -> WeatherCondition:
        print(f"[HTTP] GET https://api.openweathermap.org/data/2.5/weather?q={city}")

        # Simulamos un JSON sucio que llega de la red
        api_response_json = {
            "main": {"temp": 285.15},  # Kelvin!
            "weather": [{"main": "Rain"}],
        }

        # RESPONSABILIDAD DEL ADAPTADOR:
        # Traducir la basura del mundo exterior a la pureza del modelo del Core.
        temp_c = api_response_json["main"]["temp"] - 273.15
        is_rain = api_response_json["weather"][0]["main"] == "Rain"

        # Retorna el modelo que el Core (TripAnalyzer) exige
        return WeatherCondition(temp_celsius=temp_c, is_raining=is_rain)


# ==============================================================================
# [CAPA 3: APLICACIÓN / MAIN] (El Ensamblador)
# ==============================================================================
if __name__ == "__main__":
    adapter = OpenWeatherAdapter()
    core_service = TripAnalyzer(weather_api=adapter)

    city = "Bilbao"
    bring_umbrella = core_service.should_take_umbrella(city)
    print(f"Llevar paraguas en {city}? {'Si' if bring_umbrella else 'No'}")
