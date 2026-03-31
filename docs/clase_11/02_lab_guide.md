# Lab Guide Clase 11 — IA Local y Fallback en PyCommute

## Objetivo

Al terminar este lab, PyCommute usa Gemini como adaptador principal
y Ollama como fallback local. Si Gemini falla, el sistema conmuta
automáticamente — sin cambiar una línea del servicio.

---

## Paso 1 — Instalar Ollama y descargar el modelo

```bash
# Windows: descargar e instalar desde https://ollama.com/download
# Linux:
curl -fsSL https://ollama.com/install.sh | sh

# Verificar que está corriendo
ollama list

# Descargar el modelo que usaremos
ollama pull gemma3:1b
```

Verificar:
```bash
ollama run gemma3:1b "Di hola en español"
# → debe responder algo como "Hola"
```

---

## Paso 2 — Agregar dependencia ollama

Desde la raíz del repo:

```bash
# Windows (PowerShell)
uv add ollama

# Linux
uv add ollama
```

Verificar en `pyproject.toml`:
```toml
# Clase 11 — IA local
"ollama>=0.6.1",
```

---

## Paso 3 — Crear OllamaAdapter

Crear `curso/src/pycommute/adapters/ollama_adapter.py`.

Aplicamos la sección **2 (ollama SDK)** de `01_conceptos.md`.

El adaptador tiene la misma firma que `GeminiAdapter` — implementa `AIPort`:
```python
class OllamaAdapter:
    def __init__(self, model: str = "gemma3:1b", base_url: str = ...) -> None: ...

    async def get_recommendation(
        self,
        origin_city: str,
        destination_city: str,
        origin_weather: WeatherData,
        destination_weather: WeatherData,
        routes: list[RouteData],
    ) -> AIRecommendation: ...
```

Puntos clave del adaptador:
- `ollama.AsyncClient(host=base_url)` — async, compatible con anyio
- Mismo `_SYSTEM_PROMPT` y `_RECOMMENDATION_SCHEMA` que `GeminiAdapter`
- `response.message.content` (no `response.text` como en Gemini)
- `_clean_json()` — idéntico al de Gemini, Ollama también añade markdown

---

## Paso 4 — Crear FallbackAIAdapter

Crear `curso/src/pycommute/adapters/fallback_ai.py`.

Aplicamos la sección **3 (patrón Fallback)** de `01_conceptos.md`.

```python
class FallbackAIAdapter:
    def __init__(self, primary: AIPort, secondary: AIPort) -> None:
        self._primary = primary
        self._secondary = secondary

    async def get_recommendation(self, ...) -> AIRecommendation:
        try:
            logger.info("Intentando con {adapter}...", adapter=...)
            result = await self._primary.get_recommendation(...)
            logger.info("{adapter} respondio correctamente", adapter=...)
            return result
        except Exception as e:
            logger.warning("{primary} fallo: {error} — conmutando a {secondary}", ...)
            result = await self._secondary.get_recommendation(...)
            logger.info("{adapter} respondio correctamente", adapter=...)
            return result
```

---

## Paso 5 — Crear tests

Crear `curso/tests/unit/test_ollama.py` con 3 tests:

```python
# Test 1: OllamaAdapter devuelve AIRecommendation válida
# Mock: patch("ollama.AsyncClient") → mock_client.chat AsyncMock

# Test 2: OllamaAdapter maneja markdown en respuesta
# Mock: devolver JSON envuelto en ```json...```

# Test 3: OllamaAdapter propaga ConnectionError si Ollama no está
# Mock: mock_client.chat = AsyncMock(side_effect=ConnectionError(...))
```

Crear `curso/tests/unit/test_fallback_ai.py` con 4 tests:

```python
# Test 1: usa primario cuando funciona
# Test 2: conmuta a secundario cuando primario falla
# Test 3: propaga error si ambos fallan
# Test 4: secundario NO se llama si primario funciona
```

Verificar:
```bash
# Windows (PowerShell)
uv run pytest tests/ -v

# Linux
uv run pytest tests/ -v
```

---

## Paso 6 — Actualizar demo_proyecto.py

Crear `curso/scripts/clase_11/demo_proyecto.py`.

```python
# Construir los adaptadores
ollama_adapter = OllamaAdapter(
    model=settings.ollama_model,
    base_url=settings.ollama_base_url,
)
gemini_adapter = GeminiAdapter(
    api_key=settings.google_api_key,
    model=settings.gemini_model,
)
ai_adapter = FallbackAIAdapter(
    primary=gemini_adapter,
    secondary=ollama_adapter,
)

# El servicio recibe un AIPort — no sabe cuál
service = CommuteService(..., ai=ai_adapter)
```

---

## Paso 7 — Verificar el hito

**Demo normal (Gemini disponible):**

```bash
# Windows (PowerShell)
cd curso
uv run python scripts/clase_11/demo_proyecto.py

# Linux
cd curso
uv run python scripts/clase_11/demo_proyecto.py
```

Salida esperada:
```
INFO | FallbackAIAdapter configurado: GeminiAdapter -> OllamaAdapter (gemma3:1b)
INFO | Intentando con GeminiAdapter...
INFO | GeminiAdapter respondio correctamente
INFO | Transporte sugerido: driving-car (confianza: alta)
```

**Demo con fallback forzado:**

Editar `.env`:
```
GOOGLE_API_KEY=invalid_key_para_demostrar_fallback
```

Ejecutar de nuevo. Salida esperada:
```
INFO    | Intentando con GeminiAdapter...
WARNING | GeminiAdapter fallo: 401 — conmutando a OllamaAdapter
INFO    | Consultando Ollama (gemma3:1b) para viaje Valencia -> Madrid
INFO    | OllamaAdapter respondio correctamente
INFO    | Transporte sugerido: driving-car (confianza: media)
```

Restaurar la API key real en `.env`.

---

## ¿Por qué construimos esto así?

### La historia del AIPort

En **Clase 8** definimos `AIPort` como un `Protocol`:
```python
class AIPort(Protocol):
    async def get_recommendation(self, ...) -> AIRecommendation: ...
```

En ese momento no había ningún adaptador de IA. Era una apuesta:
*"En algún momento querremos intercambiar proveedores de IA."*

En **Clase 10** llegó `GeminiAdapter` — el primero en implementar `AIPort`.
En **Clase 11** llegan `OllamaAdapter` y `FallbackAIAdapter`.

Los tres implementan `AIPort` — los tres son sustituibles entre sí.
`CommuteService` nunca cambió. Eso es exactamente el valor de los puertos.

### ¿Por qué FallbackAIAdapter es un adaptador y no lógica en CommuteService?

Podríamos haber puesto el `try/except` directamente en `CommuteService`:
```python
# En CommuteService
try:
    rec = await self._gemini.get_recommendation(...)
except Exception:
    rec = await self._ollama.get_recommendation(...)
```

Esto funciona. Pero tiene un costo: `CommuteService` ahora conoce
dos implementaciones concretas en lugar de una abstracción.
Si añadimos un tercer proveedor (Anthropic, OpenAI), modificamos el servicio.

Con `FallbackAIAdapter`:
- La lógica de fallback está en un lugar, testeable por separado
- `CommuteService` sigue recibiendo un `AIPort` — sin cambios
- Añadir un tercer proveedor → solo cambiar `FallbackAIAdapter`

### La conexión con Clase 12

En la próxima clase exponemos `CommuteService` como API REST con FastAPI.
`FallbackAIAdapter` se inyecta igual que cualquier otra dependencia.
FastAPI no sabe si el adaptador de IA es Gemini, Ollama o el Fallback —
solo sabe que implementa `AIPort`.

**La arquitectura hexagonal acaba de demostrar su valor: añadir FastAPI
no requiere tocar el dominio ni los adaptadores existentes.**

---

## Snapshot de esta clase

```
snapshots/clase_11/
├── src/pycommute/
│   └── adapters/
│       ├── ollama_adapter.py   ← [CLASE 11] nuevo
│       └── fallback_ai.py      ← [CLASE 11] nuevo, [CLASE 12 →]
└── tests/
    └── unit/
        ├── test_ollama.py
        └── test_fallback_ai.py
```

El snapshot preserva el estado al cierre de Clase 11.
`src/` siempre contiene el código limpio y actual.
