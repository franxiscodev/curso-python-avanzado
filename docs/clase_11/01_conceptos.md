# Conceptos — Clase 11: IA Local con Ollama y Patrón Fallback

PyCommute usa Gemini para generar recomendaciones en lenguaje natural.
Pero Gemini depende de internet y de una cuota diaria gratuita.
Si la cuota se agota durante una demo — o el alumno está en el metro —
el sistema falla y no devuelve nada.

Ollama resuelve esto: un servidor de IA que corre en la máquina local,
sin internet, sin API key, sin límite de cuota.

---

## 1. Ollama — IA local sin dependencias externas

Ollama descarga modelos de lenguaje en formato GGUF (cuantizados, comprimidos)
y los sirve vía una **API REST en `localhost:11434`**. Una vez descargado el
modelo, funciona completamente offline.

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma3:1b      # 815 MB — funciona en VMs con 4 GB RAM
ollama serve               # si no está como servicio del sistema

# Windows (PowerShell)
# Instalar desde https://ollama.com/download
ollama pull gemma3:1b
ollama serve
```

**La API REST de Ollama:**

| Endpoint | Uso |
|----------|-----|
| `POST /api/generate` | Completar texto sin historial de chat |
| `POST /api/chat` | Chat con historial de mensajes |
| `GET /api/tags` | Listar modelos descargados |

**Ventajas frente a Gemini para el fallback:**

| Aspecto | Gemini | Ollama |
|---------|--------|--------|
| Internet | Requerido | No necesario |
| API key | Requerida | No necesaria |
| Cuota | Limitada (plan gratuito) | Sin límite |
| Privacidad | Datos salen a Google | Datos en tu máquina |
| Calidad | Alta | Aceptable (gemma3:1b) |

Para PyCommute, Ollama es el plan B — siempre disponible cuando Gemini falla.

---

## 2. Llamadas a Ollama via HTTP con httpx

PyCommute ya usa `httpx` para llamar a OpenWeather y ORS. La misma librería
sirve para llamar a la API REST de Ollama — no hace falta el SDK `ollama`.

```python
import httpx

async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "gemma3:1b",
            "prompt": "¿Qué ropa llevar con lluvia intensa?",
            "stream": False,   # respuesta completa, no streaming
        },
    )
    response.raise_for_status()
    texto = response.json()["response"]   # el texto generado
```

`stream=False` espera la respuesta completa antes de devolver —
es necesario para parsear el JSON completo con Pydantic.

Si Ollama no está corriendo, `httpx` lanza `ConnectError`. Capturarlo
explícitamente permite dar un mensaje de error claro al usuario.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_11/conceptos/01_ollama_basico.py`

### Analiza la salida

El script define `OllamaGateway` con dos parámetros de configuración:
`base_url` (por defecto `http://127.0.0.1:11434`) y `timeout` (30 segundos).

`generate_text` construye el payload con `stream=False` y hace el POST.
`response.raise_for_status()` lanza `HTTPStatusError` si Ollama responde con
un status no 2xx (por ejemplo, modelo no descargado → 404).

`response.json()["response"]` extrae el texto del campo específico de la
respuesta de Ollama — su estructura es diferente a la de Gemini.

`httpx.ConnectError` captura el caso más frecuente en el lab: Ollama no
está corriendo. El `logger.critical` da instrucción exacta al alumno: `ollama serve`.

---

## 3. Salida estructurada de Ollama con Pydantic

Para integrar la respuesta de Ollama con el resto de PyCommute necesitamos
JSON válido, no texto libre. El parámetro `format="json"` de Ollama fuerza
al modelo a devolver JSON sin bloques markdown.

```python
from pydantic import BaseModel, Field, ValidationError

class WeatherAdvice(BaseModel):
    risk_level: str = Field(description="Nivel de riesgo: 'Bajo', 'Medio' o 'Alto'")
    actionable_tip: str = Field(description="Consejo práctico de conducción")

# En el payload al POST:
json={
    "model": "gemma3:1b",
    "prompt": "Genera consejo para lluvia intensa. Responde en JSON con 'risk_level' y 'actionable_tip'.",
    "format": "json",
    "stream": False,
}

raw_json = response.json()["response"]   # string JSON de Ollama
advice = WeatherAdvice.model_validate_json(raw_json)  # parsea + valida
```

El prompt debe nombrar explícitamente los campos del schema — los modelos
pequeños como `gemma3:1b` son más fiables cuando el prompt es concreto.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_11/conceptos/02_ollama_structured.py`

### Analiza la salida

`WeatherAdvice` define dos campos con `description` — las descriptions
guían al modelo sobre qué valor poner en cada campo.

`get_structured_advice` construye un prompt que pide explícitamente los
nombres de las llaves JSON. `format="json"` en el payload evita que Ollama
añada texto fuera del JSON (algo que los modelos pequeños hacen con frecuencia).

`WeatherAdvice.model_validate_json(raw_json)` es la frontera: si el modelo
devuelve `{"risk_level": "Extremo", ...}` (valor no esperado), `ValidationError`
aparece aquí — no en el servicio. El `logger.error` registra qué devolvió
el modelo para facilitar el diagnóstico.

---

## 4. Patrón Fallback con reintentos

El fallback resuelve: **¿qué hace el sistema cuando el proveedor principal falla?**
En PyCommute, el proveedor principal es Gemini. El fallback es Ollama.

```python
async def orchestrate_ai(prompt: str) -> str:
    try:
        return await try_cloud_with_retries(prompt)   # intenta Gemini N veces
    except QuotaExceededError as e:
        logger.warning(f"Fallback activado: {e}")
        return await fallback_local_ai(prompt)        # conmuta a Ollama
```

**El rol de `tenacity` en los reintentos:**

```python
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=5),
    retry=retry_if_exception_type(QuotaExceededError),
    reraise=True,    # propaga la excepción original tras agotar los intentos
)
async def try_cloud_with_retries(prompt: str) -> str:
    return await primary_cloud_ai(prompt)
```

`reraise=True` es crítico: sin él, tenacity lanza `RetryError` en lugar de
`QuotaExceededError`, y el `except QuotaExceededError` del orquestador no la captura.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_11/conceptos/03_patron_fallback.py`

### Analiza la salida

El script define `primary_cloud_ai` que siempre lanza `QuotaExceededError`
(simula Gemini con cuota agotada) y `fallback_local_ai` que siempre tiene éxito
(simula Ollama).

`try_cloud_with_retries` tiene `stop_after_attempt(2)` — reintenta una vez
antes de rendirse. En el output se ven dos intentos al cloud antes del fallback.

`orchestrate_ai` captura `QuotaExceededError` y delega a `fallback_local_ai`.
El `logger.warning` con el motivo del fallo es la trazabilidad que permite
diagnosticar cuándo y por qué el sistema conmutó al proveedor local.

---

## 5. Resiliencia bajo carga concurrente

El patrón fallback debe funcionar igual con 1 petición que con 10 en paralelo.
`anyio.create_task_group` permite verificarlo sin infraestructura real.

```python
async def run_benchmark():
    results = []
    async with anyio.create_task_group() as tg:
        for i in range(1, 11):
            tg.start_soon(process_request, i, results)
    # Cuando el bloque termina, todas las peticiones han completado
    cloud_count = sum(1 for r in results if r[1] == "Cloud_Data")
    local_count = sum(1 for r in results if r[1] == "Local_Data")
```

El `create_task_group` garantiza que cuando el bloque `async with` termina,
todas las tareas han finalizado — es la concurrencia estructurada de Clase 5.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_11/conceptos/04_resiliencia_comparativa.py`

### Analiza la salida

`flaky_cloud` falla el 60% de las veces con un `await anyio.sleep(0.2)` de latencia.
`reliable_local` nunca falla, pero tiene `await anyio.sleep(0.8)` — 4x más lento.

`process_request` orquesta el fallback por petición individual: intenta cloud,
captura `QuotaExceededError`, llama a local. El patrón es idéntico al del
script anterior — solo cambia que se ejecuta 10 veces en paralelo.

El reporte final muestra `{N}/10 (100% Uptime)` — ninguna petición se perdió.
La distribución entre cloud y local varía en cada ejecución (el 60% de fallos
es aleatorio), pero el total siempre es 10.

---

## 6. Circuit Breaker vs Fallback simple y LSP

### Circuit Breaker vs Fallback simple

El fallback que implementamos tiene un coste: **cada petición paga el tiempo
del intento fallido al proveedor principal**.

| Situación | Recomendación |
|-----------|--------------|
| Fallos esporádicos (cuota diaria) | Fallback simple |
| Proveedor caído por horas | Circuit Breaker |
| Alto volumen (>100 req/min) | Circuit Breaker |
| Prototipo / curso | Fallback simple |

Un Circuit Breaker añade tres estados (CLOSED → OPEN → HALF-OPEN) para evitar
intentar el proveedor caído. Para PyCommute los fallos son esporádicos y el
overhead de un intento fallido es tolerable.

### Principio de Sustitución de Liskov (LSP)

El patrón fallback solo funciona porque `GeminiAdapter`, `OllamaAdapter` y
`FallbackAIAdapter` son **intercambiables** — todos implementan `AIPort`:

```python
from typing import Protocol

class AIPort(Protocol):
    async def get_recommendation(self, ...) -> AIRecommendation: ...

# Todos son válidos — CommuteService no sabe cuál está usando
servicio = CommuteService(ai=GeminiAdapter(...))
servicio = CommuteService(ai=OllamaAdapter(...))
servicio = CommuteService(ai=FallbackAIAdapter(...))
```

LSP va más allá de la firma del método. Un adaptador que siempre lanza
`NotImplementedError` tiene la firma correcta pero viola el contrato implícito:
el llamador espera una `AIRecommendation` válida, no una excepción no recuperable.

`AIPort` se definió en Clase 8. Esa decisión hace posible el fallback hoy.
