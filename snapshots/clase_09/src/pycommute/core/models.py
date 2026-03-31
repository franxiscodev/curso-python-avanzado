"""Modelos de dominio de PyCommute — contratos de datos con Pydantic V2.

# [CLASE 9] Archivo nuevo. Antes (Clase 8) los adaptadores devolvian
# dict[str, Any] — contratos implicitos sin validacion.
# WeatherData y RouteData garantizan que los datos son validos
# en el momento en que cruzan la frontera del adaptador.
# ConsultaEntry reemplaza el @dataclass de Clase 7.
# [CLASE 10 ->] CommuteResult.model_dump() se enviara a Gemini API
# como contexto estructurado para el analisis de movilidad.

Estos modelos son la unica fuente de verdad sobre que datos
fluyen entre las capas del sistema. Si un adaptador devuelve
datos invalidos, Pydantic lo detecta en la frontera — no en
la logica de negocio.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class RouteProfile(str, Enum):
    """Perfiles de ruta soportados por OpenRouteService."""

    CYCLING = "cycling-regular"
    DRIVING = "driving-car"
    WALKING = "foot-walking"


class WeatherData(BaseModel):
    """Datos de clima validados — contrato entre OpenWeatherAdapter y el core."""

    temperature: float = Field(description="Temperatura en grados Celsius")
    description: str = Field(min_length=1, description="Descripcion del clima")
    city: str = Field(min_length=1, description="Nombre de la ciudad")

    @field_validator("temperature")
    @classmethod
    def temperature_realistic(cls, v: float) -> float:
        """Valida que la temperatura este en un rango realista."""
        if not -80 <= v <= 60:
            raise ValueError(
                f"Temperatura irrealista: {v}C "
                f"(rango valido: -80C a 60C)"
            )
        return round(v, 1)

    @field_validator("description")
    @classmethod
    def description_lowercase(cls, v: str) -> str:
        """Normaliza la descripcion a minusculas."""
        return v.lower().strip()


class RouteData(BaseModel):
    """Datos de ruta validados — contrato entre OpenRouteAdapter y el core."""

    distance_km: float = Field(gt=0, description="Distancia en kilometros")
    duration_min: float = Field(gt=0, description="Duracion en minutos")
    profile: str = Field(description="Perfil de transporte")

    @field_validator("profile")
    @classmethod
    def profile_valid(cls, v: str) -> str:
        """Valida que el perfil sea uno de los soportados."""
        valid = {p.value for p in RouteProfile}
        if v not in valid:
            raise ValueError(
                f"Perfil invalido: '{v}'. "
                f"Perfiles validos: {valid}"
            )
        return v


class CommuteResult(BaseModel):
    """Resultado completo de una consulta de movilidad."""

    weather: WeatherData
    routes: list[RouteData] = Field(min_length=1)
    best_route: RouteData | None = None

    @model_validator(mode="after")
    def set_best_route(self) -> "CommuteResult":
        """Calcula la mejor ruta (menor tiempo) automaticamente."""
        if self.routes and self.best_route is None:
            self.best_route = min(self.routes, key=lambda r: r.duration_min)
        return self


class ConsultaEntry(BaseModel):
    """Entrada del historial — reemplaza el dataclass de Clase 7."""

    timestamp: datetime = Field(default_factory=datetime.now)
    city: str
    profiles: list[str]
    result: CommuteResult

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M")
        profiles_str = ", ".join(self.profiles)
        return f"[{ts}] {self.city} -> {profiles_str}"
