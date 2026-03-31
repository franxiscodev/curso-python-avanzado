# Lab Guide — Clase 09: Contratos de Datos con Pydantic V2

## La historia de los contratos en PyCommute

**Clase 2** — Los adaptadores devolvían `dict[str, Any]`:
```python
return {"temperature": temp, "description": desc, "city": city}
```
Flexible. Sin garantías. Un typo en la clave (`"temp"` en lugar de `"temperature"`)
pasa desapercibido hasta que algo explota en producción.

**Clase 8** — Introdujimos `Protocol` para contratos de **comportamiento**:
```python
class WeatherPort(Protocol):
    async def get_current_weather(self, city: str, api_key: str) -> dict: ...
```
Ahora sabemos **qué operaciones** puede hacer un adaptador.
Pero el `dict` que devuelve sigue siendo opaco.

**Clase 9** — Pydantic para contratos de **datos**:
```python
class WeatherPort(Protocol):
    async def get_current_weather(self, city: str, api_key: str) -> WeatherData: ...
```
Comportamiento + datos = sistema de tipos completo.

---

## Dependencias

```bash
uv add pydantic
```

En `pyproject.toml`, la dependencia aparece con el comentario `# Clase 9`.

---

## Paso 1 — Crear `core/models.py`

Crea el archivo `src/pycommute/core/models.py`. Este archivo es **la única fuente
de verdad** sobre qué datos fluyen entre las capas del sistema.

### RouteProfile — perfiles válidos como Enum

```python
from enum import Enum

class RouteProfile(str, Enum):
    CYCLING = "cycling-regular"
    DRIVING = "driving-car"
    WALKING = "foot-walking"
```

Hereda de `str` para que los valores sean strings directamente:
`RouteProfile.CYCLING == "cycling-regular"` es `True`.

### WeatherData

```python
from pydantic import BaseModel, Field, field_validator

class WeatherData(BaseModel):
    temperature: float = Field(description="Temperatura en grados Celsius")
    description: str = Field(min_length=1, description="Descripcion del clima")
    city: str = Field(min_length=1, description="Nombre de la ciudad")

    @field_validator("temperature")
    @classmethod
    def temperature_realistic(cls, v: float) -> float:
        if not -80 <= v <= 60:
            raise ValueError(
                f"Temperatura irrealista: {v}C "
                f"(rango valido: -80C a 60C)"
            )
        return round(v, 1)

    @field_validator("description")
    @classmethod
    def description_lowercase(cls, v: str) -> str:
        return v.lower().strip()
```

### RouteData

```python
class RouteData(BaseModel):
    distance_km: float = Field(gt=0, description="Distancia en kilometros")
    duration_min: float = Field(gt=0, description="Duracion en minutos")
    profile: str = Field(description="Perfil de transporte")

    @field_validator("profile")
    @classmethod
    def profile_valid(cls, v: str) -> str:
        valid = {p.value for p in RouteProfile}
        if v not in valid:
            raise ValueError(
                f"Perfil invalido: '{v}'. "
                f"Perfiles validos: {valid}"
            )
        return v
```

### CommuteResult con model_validator

```python
from pydantic import model_validator

class CommuteResult(BaseModel):
    weather: WeatherData
    routes: list[RouteData] = Field(min_length=1)
    best_route: RouteData | None = None

    @model_validator(mode="after")
    def set_best_route(self) -> "CommuteResult":
        if self.routes and self.best_route is None:
            self.best_route = min(self.routes, key=lambda r: r.duration_min)
        return self
```

### ConsultaEntry — reemplaza el dataclass de Clase 7

```python
from datetime import datetime

class ConsultaEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    city: str
    profiles: list[str]
    result: CommuteResult

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M")
        profiles_str = ", ".join(self.profiles)
        return f"[{ts}] {self.city} -> {profiles_str}"
```

La diferencia respecto al `@dataclass` de Clase 7: `entry.model_dump(mode="json")`
devuelve un dict completamente serializable, incluyendo `datetime` como string ISO.

---

## Paso 2 — Actualizar los puertos

En `core/ports.py`, cambia el tipo de retorno de `dict` a los modelos Pydantic:

```python
from pycommute.core.models import RouteData, WeatherData

class WeatherPort(Protocol):
    async def get_current_weather(self, city: str, api_key: str) -> WeatherData: ...

class RoutePort(Protocol):
    async def get_route(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        profile: str,
        api_key: str,
    ) -> RouteData: ...
```

---

## Paso 3 — Actualizar el adaptador de clima

En `adapters/weather.py`, en lugar de devolver un `dict`, construye un `WeatherData`:

```python
from pycommute.core.models import WeatherData

# Antes:
return {"temperature": temp, "description": desc, "city": city}

# Ahora:
return WeatherData(temperature=temp, description=desc, city=city)
```

Si los datos de OpenWeather son inválidos (temperatura fuera de rango, descripción
vacía), `ValidationError` se lanza **aquí** — en el adaptador, en la frontera.
No en el servicio. No en el historial.

---

## Paso 4 — Actualizar el adaptador de rutas

En `adapters/route.py`, en lugar de devolver un `dict`, construye un `RouteData`:

```python
from pycommute.core.models import RouteData

# Antes:
return {"distance_km": round(dist / 1000, 1), "duration_min": round(dur / 60), "profile": profile}

# Ahora:
return RouteData(
    distance_km=round(dist / 1000, 1),
    duration_min=round(dur / 60),
    profile=profile,
)
```

---

## Paso 5 — Actualizar el servicio

En `services/commute.py`, actualiza la firma de retorno y la construcción del resultado:

```python
from pycommute.core.models import CommuteResult, ConsultaEntry, RouteData, WeatherData

async def get_commute_info(self, ...) -> CommuteResult:
    weather_data: WeatherData | None = None
    route_list: list[RouteData] = []

    async def fetch_weather() -> None:
        nonlocal weather_data
        weather_data = await self._weather.get_current_weather(city, weather_key)

    # ... fetch en paralelo ...

    result = CommuteResult(weather=weather_data, routes=route_list)
    # best_route se calcula automáticamente en el model_validator

    self._history.add(
        ConsultaEntry(city=city, profiles=profiles, result=result)
    )
    return result
```

---

## Paso 6 — Actualizar ranking.py

`rank_routes_by_time` y `get_best_route` trabajan con `list[RouteData]`.
Cambia el acceso de dict (`route["duration_min"]`) a atributo (`route.duration_min`):

```python
from pycommute.core.models import RouteData

def rank_routes_by_time(routes: list[RouteData]) -> list[RouteData]:
    heap: list[tuple[float, int, RouteData]] = []
    for i, route in enumerate(routes):
        heapq.heappush(heap, (route.duration_min, i, route))
    # ...

def get_best_route(routes: list[RouteData], by: str = "time") -> RouteData:
    best = heapq.nsmallest(1, routes, key=lambda r: getattr(r, key))[0]
```

---

## Paso 7 — Actualizar history.py

`ConsultaHistory.add()` ahora recibe un `ConsultaEntry` completo:

```python
from pycommute.core.models import ConsultaEntry

class ConsultaHistory:
    def add(self, entry: ConsultaEntry) -> None:
        self._history.append(entry)
```

---

## Paso 8 — Escribir tests en `tests/unit/test_models.py`

Crea el archivo con al menos estos cinco tests:

```python
from pydantic import ValidationError
import pytest
from pycommute.core.models import (
    CommuteResult, ConsultaEntry, RouteData, WeatherData
)

def test_weather_data_normaliza_description():
    w = WeatherData(temperature=13.5, description="  Clear Sky  ", city="Valencia")
    assert w.description == "clear sky"

def test_weather_data_rechaza_temperatura_irrealista():
    with pytest.raises(ValidationError, match="Temperatura irrealista"):
        WeatherData(temperature=999.0, description="hot", city="Venus")

def test_route_data_rechaza_perfil_invalido():
    with pytest.raises(ValidationError, match="Perfil invalido"):
        RouteData(distance_km=2.0, duration_min=8.0, profile="flying-car")

def test_commute_result_calcula_best_route_automaticamente():
    cycling = RouteData(distance_km=5.0, duration_min=22.0, profile="cycling-regular")
    driving = RouteData(distance_km=4.8, duration_min=5.0, profile="driving-car")
    result = CommuteResult(
        weather=WeatherData(temperature=13.0, description="clear sky", city="Valencia"),
        routes=[cycling, driving],
    )
    assert result.best_route.profile == "driving-car"

def test_consulta_entry_serializable():
    entry = ConsultaEntry(
        city="Valencia",
        profiles=["cycling-regular"],
        result=CommuteResult(
            weather=WeatherData(temperature=13.0, description="clear sky", city="Valencia"),
            routes=[RouteData(distance_km=5.0, duration_min=22.0, profile="cycling-regular")],
        ),
    )
    data = entry.model_dump(mode="json")
    assert isinstance(data["timestamp"], str)  # ISO string, no objeto datetime
    assert "result" in data
```

---

## Paso 9 — Actualizar los tests existentes

Los tests de `test_weather.py`, `test_route.py`, `test_ranking.py`, `test_history.py`
y `test_commute.py` usan dicts o firmas antiguas. Actualiza:

- `test_weather.py`: `assert isinstance(result, WeatherData)`, acceso por atributo
- `test_route.py`: `assert isinstance(result, RouteData)`, acceso por atributo
- `test_ranking.py`: `ROUTES: list[RouteData]`, `.duration_min` en lugar de `["duration_min"]`
- `test_history.py`: helper `_entry()` que devuelve `ConsultaEntry`
- `test_commute.py`: `WEATHER_RESULT = WeatherData(...)`, `ROUTE_RESULT = RouteData(...)`

---

## Paso 10 — Verificar

```bash
# Windows (PowerShell)
uv run pytest tests/ -v

# Linux
uv run pytest tests/ -v
```

Resultado esperado: **36 tests passing** (+5 nuevos en `test_models.py`).

---

## Paso 11 — Demo del hito

```bash
# Windows (PowerShell)
uv run scripts/clase_09/demo_proyecto.py

# Linux
uv run scripts/clase_09/demo_proyecto.py
```

Verás ValidationError en la frontera para temperatura de 999°C y perfil "flying-car",
y el CommuteResult con `best_route` calculada automáticamente.

---

## ¿Por qué construimos esto así?

### dict → dataclass → Pydantic: la evolución completa

Clase 2 introdujo `dict[str, Any]` — rápido de escribir, sin fricción.
Clase 7 introdujo `@dataclass` para `ConsultaEntry` — estructura, pero sin validación.
Clase 8 introdujo `Protocol` — contratos de comportamiento entre capas.
Clase 9 cierra el ciclo con Pydantic — contratos de datos.

La pregunta que justifica Pydantic es: "¿dónde falla si la API devuelve 999°C?"
Con dict, no falla. El dato inválido llega al servicio, al historial, al output.
Con Pydantic, falla en `WeatherData(temperature=999.0)` — en el adaptador,
antes de que el dato entre al sistema.

### Por qué `model_validator` para `best_route`

Sin `model_validator`, el llamador debe calcular `best_route` después de crear el objeto:
```python
result = CommuteResult(weather=weather, routes=routes)
result.best_route = min(routes, key=lambda r: r.duration_min)  # fácil de olvidar
```

Con `model_validator(mode="after")`, `best_route` siempre existe cuando
el objeto existe. Es un **invariante del modelo** — el objeto garantiza
su propio estado consistente.

### Por qué `ConsultaEntry` migra de dataclass a Pydantic

El dataclass de Clase 7 no se podía serializar a JSON directamente.
Con Pydantic, `entry.model_dump(mode="json")` devuelve un dict completamente
serializable, incluyendo `datetime` como string ISO.
Esto es preparación directa para Clase 12, donde el historial se expondrá via FastAPI.

### La conexión con Clase 10

```python
result.model_dump(mode="json")
# {
#   "weather": {"temperature": 13.0, "description": "clear sky", "city": "Valencia"},
#   "routes": [...],
#   "best_route": {"profile": "driving-car", "duration_min": 5.0, ...}
# }
```

Este dict estructurado es el contexto que enviaremos a Gemini API.
Un LLM puede entender `best_route.profile` como "la recomendación de PyCommute".
Con un dict anónimo sin estructura, no hay contexto para el modelo de lenguaje.

---

## Referencia al snapshot

El estado completo de esta clase está en:
```
curso/snapshots/clase_09/
├── src/pycommute/
│   ├── core/
│   │   ├── models.py        ← archivo nuevo de esta clase
│   │   ├── ports.py         ← tipos actualizados a WeatherData/RouteData
│   │   ├── ranking.py       ← acceso por atributo
│   │   └── history.py       ← ConsultaEntry Pydantic
│   ├── adapters/
│   │   ├── weather.py       ← devuelve WeatherData
│   │   └── route.py         ← devuelve RouteData
│   └── services/
│       └── commute.py       ← devuelve CommuteResult
└── tests/
    └── unit/
        └── test_models.py   ← tests nuevos de esta clase
```

Los snapshots son de solo lectura — preservan el estado exacto al cerrar la clase.
