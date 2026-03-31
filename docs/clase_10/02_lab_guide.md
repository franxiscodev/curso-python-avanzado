# Lab Guide — Clase 10: IA Cloud con Gemini API

## La historia de los datos en PyCommute

**Clase 2** — `dict[str, Any]`: datos sin estructura ni validación.

**Clase 8** — `Protocol`: contratos de comportamiento entre capas.

**Clase 9** — `BaseModel`: contratos de datos, validación en la frontera.
```python
# Clase 9: PyCommute devuelve datos correctos
result.origin_weather.temperature  # 13.0 — validado
result.best_route.profile          # "driving-car" — validado
```

**Clase 10** — IA: los datos correctos + lenguaje natural.
```python
# Clase 10: PyCommute ahora interpreta
result.ai_recommendation.recommendation  # "Toma el coche, hay nieve..."
result.ai_recommendation.outfit_tips     # ["abrigo", "bufanda", "paraguas"]
```

Un LLM tiene acceso a todo el contexto (`model_dump()` de Clase 9)
y lo convierte en lenguaje humano útil.

---

## Dependencias

```bash
# Windows (PowerShell) y Linux — desde la raíz del repo
uv add google-genai
```

Agregar `GOOGLE_API_KEY` al archivo `.env` en `curso/`:
```
GOOGLE_API_KEY=tu-api-key-de-google-ai-studio
```

Obtener la key en: https://aistudio.google.com/app/apikey (plan gratuito disponible).

---

## Paso 1 — Actualizar `core/models.py`

### Agregar `AIRecommendation`

```python
class AIRecommendation(BaseModel):
    recommendation: str = Field(min_length=10)
    suggested_profile: str = Field(description="Perfil de transporte sugerido")
    confidence: str = Field(description="Nivel de confianza: alta, media o baja")
    reasoning: str = Field(min_length=5)
    outfit_tips: list[str] = Field(default_factory=list)
    departure_advice: str = Field(default="")

    @field_validator("confidence")
    @classmethod
    def confidence_valid(cls, v: str) -> str:
        valid = {"alta", "media", "baja"}
        if v.lower() not in valid:
            raise ValueError(f"Confianza invalida: '{v}'. Usar: {valid}")
        return v.lower()

    @field_validator("suggested_profile")
    @classmethod
    def profile_valid(cls, v: str) -> str:
        valid = {p.value for p in RouteProfile}
        if v not in valid:
            raise ValueError(f"Perfil invalido: '{v}'")
        return v
```

### Actualizar `CommuteResult`

```python
class CommuteResult(BaseModel):
    origin_city: str
    destination_city: str
    origin_weather: WeatherData      # antes: solo weather
    destination_weather: WeatherData  # nuevo — clima del destino
    routes: list[RouteData] = Field(min_length=1)
    best_route: RouteData | None = None
    ai_recommendation: AIRecommendation | None = None  # nuevo

    @model_validator(mode="after")
    def set_best_route(self) -> "CommuteResult":
        if self.routes and self.best_route is None:
            self.best_route = min(self.routes, key=lambda r: r.duration_min)
        return self
```

---

## Paso 2 — Agregar `AIPort` a `core/ports.py`

```python
from pycommute.core.models import AIRecommendation, RouteData, WeatherData

@runtime_checkable
class AIPort(Protocol):
    async def get_recommendation(
        self,
        origin_city: str,
        destination_city: str,
        origin_weather: WeatherData,
        destination_weather: WeatherData,
        routes: list[RouteData],
    ) -> AIRecommendation: ...
```

---

## Paso 3 — Crear `adapters/gemini.py`

```python
from google import genai
from google.genai import types

_SYSTEM_PROMPT = """Eres un asistente de movilidad urbana experto.
Responde SIEMPRE en español y en formato JSON válido."""

_RECOMMENDATION_SCHEMA = {
    "recommendation": "string — recomendación principal (mín 10 palabras)",
    "suggested_profile": "cycling-regular | driving-car | foot-walking",
    "confidence": "alta | media | baja",
    "reasoning": "string — razonamiento breve",
    "outfit_tips": "array de strings",
    "departure_advice": "string — consejo de salida",
}

class GeminiAdapter:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._config = types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
        )
```

El método `get_recommendation()` construye el prompt con `_build_prompt()`,
llama a `client.aio.models.generate_content()`, limpia el markdown con
`_clean_json()`, parsea con `json.loads()` y valida con `AIRecommendation(**data)`.

---

## Paso 4 — Actualizar `services/commute.py`

### Constructor con `AIPort` opcional

```python
def __init__(
    self,
    weather: WeatherPort,
    route: RoutePort,
    cache: CachePort,
    history: ConsultaHistory | None = None,
    ai: AIPort | None = None,  # nuevo
) -> None:
    self._ai = ai
```

### 3 tareas en paralelo + IA después

```python
results: dict[str, Any] = {}

async def fetch_origin_weather() -> None:
    results["origin_weather"] = await self._weather.get_current_weather(...)

async def fetch_destination_weather() -> None:
    results["destination_weather"] = await self._weather.get_current_weather(...)

async def fetch_routes() -> None:
    ...

async with anyio.create_task_group() as tg:
    tg.start_soon(fetch_origin_weather)
    tg.start_soon(fetch_destination_weather)
    tg.start_soon(fetch_routes)

commute_result = CommuteResult(
    origin_city=city,
    destination_city=destination_city,
    origin_weather=results["origin_weather"],
    destination_weather=results["destination_weather"],
    routes=results["routes"],
)

if self._ai and google_key:
    commute_result.ai_recommendation = await self._ai.get_recommendation(...)
```

---

## Paso 5 — Crear `tests/fixtures/gemini_response.json`

```json
{
  "recommendation": "Toma el coche, las condiciones en Madrid son adversas con nieve",
  "suggested_profile": "driving-car",
  "confidence": "alta",
  "reasoning": "La nieve en Madrid hace que la bici y caminar sean opciones peligrosas",
  "outfit_tips": ["abrigo de invierno", "bufanda", "guantes", "paraguas"],
  "departure_advice": "Salir antes de las 14h para evitar el tráfico con nieve"
}
```

---

## Paso 6 — Crear `tests/unit/test_gemini.py`

```python
@pytest.fixture
def adapter():
    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        yield GeminiAdapter(api_key="test-key"), mock_client

@pytest.mark.anyio
async def test_get_recommendation_returns_ai_recommendation(adapter):
    gemini, mock_client = adapter
    mock_response = MagicMock()
    mock_response.text = (FIXTURES / "gemini_response.json").read_text()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    result = await gemini.get_recommendation(...)

    assert isinstance(result, AIRecommendation)
    assert result.suggested_profile == "driving-car"
```

---

## Paso 7 — Verificar

```bash
# Windows (PowerShell) y Linux
uv run pytest tests/ -v
```

Resultado esperado: **45 tests passing**.

---

## Paso 8 — Demo del hito

```bash
# Windows (PowerShell) y Linux
uv run scripts/clase_10/demo_proyecto.py
```

Salida esperada (con `GOOGLE_API_KEY` configurada):
```
INFO | Valencia: 13°C, scattered clouds
INFO | Madrid: 5°C, light snow
INFO | Transporte sugerido: driving-car (confianza: alta)
INFO | Recomendación: Toma el coche, las condiciones en Madrid...
INFO | Vestimenta: abrigo de invierno, bufanda, guantes, paraguas
INFO | Consejo de salida: Salir antes de las 14h...
```

---

## ¿Por qué construimos esto así?

### Por qué necesitamos el clima del destino

La Clase 9 solo consultaba el clima de la ciudad de origen. Un viaje Valencia → Madrid
con 13°C en Valencia y nieve en Madrid no se puede recomendar correctamente
sin saber qué pasa en el destino. Agregar la segunda consulta de clima es trivial
con `anyio.create_task_group()` — una línea más en el grupo de tareas.

### Por qué JSON en el prompt (no texto libre)

Si Gemini devuelve texto libre, hay que parsearlo con regex o heurísticas frágiles.
Si le pedimos JSON con schema explícito en el prompt, podemos construir
`AIRecommendation` directamente con la misma validación Pydantic de los
adaptadores de OpenWeather y OpenRouteService. El patrón es consistente.

### Por qué `AIPort` como Protocol (no herencia directa)

`GeminiAdapter` implementa `AIPort` por duck typing — sin herencia.
En Clase 11, `OllamaAdapter` implementará el mismo `AIPort` de la misma forma.
`CommuteService` no cambia cuando se agrega Ollama — solo el adaptador inyectado.

### Por qué `ai_recommendation` es `None | AIRecommendation`

El servicio funciona sin IA: clima y rutas son suficientes para el caso base.
La IA agrega valor pero no es un requisito. Esto facilita los tests (no necesitan
mockear Gemini cuando no pasan un `AIPort`) y es el preview del patrón fallback
de Clase 11: si Gemini falla, Ollama responde. Mismo resultado, diferente adaptador.

### La conexión con Clase 12

```python
# FastAPI expone el CommuteResult como JSON
@app.get("/commute")
async def get_commute(...) -> CommuteResult:
    return await service.get_commute_info(...)

# El response incluye ai_recommendation con todos los campos
# outfit_tips y departure_advice llegan al frontend de Clase 13
```

---

## Referencia al snapshot

El estado completo de esta clase está en:
```
curso/snapshots/clase_10/
├── src/pycommute/
│   ├── adapters/
│   │   └── gemini.py       ← nuevo
│   ├── core/
│   │   ├── models.py       ← AIRecommendation + CommuteResult actualizado
│   │   └── ports.py        ← AIPort agregado
│   └── services/
│       └── commute.py      ← 3 tareas paralelas + AI opcional
└── tests/
    ├── fixtures/
    │   └── gemini_response.json
    └── unit/
        └── test_gemini.py
```
