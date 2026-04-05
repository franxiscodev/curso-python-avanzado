# Conceptos — Clase 10: IA en la Nube con Gemini API

PyCommute ya obtiene clima y rutas, valida los datos con Pydantic y los
devuelve como `CommuteResult`. Pero "temperatura 13°C, ruta 22 minutos" es
un dato, no una recomendación. El usuario quiere saber si salir ahora en bici
o esperar al tren. Eso requiere interpretación en lenguaje natural.

Gemini es la pieza que convierte datos estructurados en consejo útil.

---

## 1. ¿Qué es un LLM y cómo influye en su uso?

Un **Large Language Model** no "entiende" el texto — predice el siguiente
token dado un contexto. Un token es aproximadamente 3-4 caracteres en español.
"Valencia" = 2 tokens.

**Ventana de contexto**: cuántos tokens puede ver el modelo a la vez.
Gemini 2.5 Flash: más de 1 millón de tokens — suficiente para incluir el
historial completo de PyCommute en cada llamada.

**Temperature**: controla la aleatoriedad de las respuestas.

| Valor | Comportamiento | Cuándo usarlo |
|-------|----------------|---------------|
| `0.0` | Determinístico, siempre el token más probable | JSON estructurado, guardrails |
| `0.2` | Casi determinístico con ligera variación | Evaluaciones, análisis |
| `1.0` | Balance entre coherencia y variedad (default) | Texto libre |
| `2.0` | Muy creativo, impredecible | Generación creativa |

Para respuestas estructuradas (JSON), usar `temperature=0.0` o `0.2`.
Con valores altos el modelo puede "alucinar" campos no pedidos o ignorar el schema.

---

## 2. Cliente Gemini SDK

El SDK de Python para Gemini es `google-genai` (el SDK anterior
`google-generativeai` está deprecado desde 2025). La diferencia principal:
el nuevo SDK usa un objeto `Client` en lugar de configuración global.

```python
from google import genai
from google.genai import types

# Un cliente por aplicación — recibe la API key explícitamente
client = genai.Client(api_key="tu-api-key")

# Llamada básica: client.models.generate_content
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="¿Debería ir en bici con lluvia?",
)
print(response.text)
```

La API key se lee del entorno con `os.getenv("GOOGLE_API_KEY")` — nunca
hardcodeada en el código. Si no existe, el proceso termina con `sys.exit(1)`.

Los errores de red o cuota se capturan con `APIError`:

```python
from google.genai.errors import APIError

try:
    response = client.models.generate_content(...)
except APIError as e:
    logger.error(f"Fallo en la API: {e.message}")
```

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_10/conceptos/01_gemini_basico.py`

### Analiza la salida

El script define `initialize_modern_client()` que:
1. Lee `GOOGLE_API_KEY` del entorno — si no está, termina con `logger.critical`
2. Crea `genai.Client(api_key=api_key)` — objeto limpio, sin estado global

En el bloque `__main__`:
- Envía `"Devuelve solo la palabra 'ACK'."` — prompt mínimo para verificar conectividad
- `response.text.strip()` devuelve exactamente lo que devolvió el modelo
- Si la API falla (red, cuota, key inválida), `APIError` lo captura con el mensaje de error

El `logger.success` confirma que la conexión funciona. Si ves `logger.error`,
el motivo está en `e.message` (normalmente `INVALID_ARGUMENT` o `RESOURCE_EXHAUSTED`).

---

## 3. Salida estructurada con Pydantic

Para integrar la respuesta del modelo con el resto de PyCommute, necesitamos
JSON validado, no texto libre. El SDK acepta una clase `BaseModel` directamente
como schema — el modelo genera JSON conforme a esa estructura.

```python
from pydantic import BaseModel, Field
from google.genai import types

class CommuteAnalysis(BaseModel):
    recommended_mode: str = Field(..., description="Modo de transporte recomendado")
    risk_level: int = Field(..., ge=1, le=5, description="Nivel de riesgo")
    reasoning: str = Field(..., description="Explicación breve")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Evalúa ir en bici por Valencia con lluvia.",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=CommuteAnalysis,   # el SDK convierte el modelo a JSON Schema
    ),
)

# model_validate_json: parsea el string y valida los tipos en un paso
analysis = CommuteAnalysis.model_validate_json(response.text)
```

Si `risk_level` llega como `6` (fuera del rango `ge=1, le=5`), Pydantic lanza
`ValidationError` en la frontera — la capa de negocio nunca recibe el dato inválido.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_10/conceptos/02_gemini_structured_output.py`

### Analiza la salida

El script define `CommuteAnalysis` con tres campos y sus constraints:
- `recommended_mode: str` — libre, el modelo elige el valor
- `risk_level: int` con `ge=1, le=5` — Pydantic valida el rango
- `reasoning: str` — explicación técnica

En `GenerateContentConfig`:
- `response_mime_type="application/json"` fuerza al modelo a no añadir markdown
- `response_schema=CommuteAnalysis` pasa el schema directamente — el SDK lo convierte

`CommuteAnalysis.model_validate_json(response.text)` es la línea clave:
parsea el JSON y valida los tipos en una sola operación. Si el modelo no siguió
el schema (raro con `response_schema`), `ValidationError` aparece aquí, no más adelante.

---

## 4. System instruction — rol y guardrails

`system_instruction` define el comportamiento del modelo para toda la sesión.
Va separado del `contents` (el prompt del usuario) — el modelo lo recibe primero.

```python
SYSTEM_PROMPT = """
ERES: El motor central de PyCommute.
OBJETIVO: Evaluar riesgos de movilidad urbana.
REGLA: Bajo ninguna circunstancia responderás a temas ajenos a la movilidad.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="¿Debería tomar la bicicleta con 45 km/h de viento?",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.0,
    ),
)
```

Con `temperature=0.0`, el modelo sigue el `system_instruction` con máxima
fidelidad — es la combinación habitual para sistemas de producción.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_10/conceptos/03_system_instruction.py`

### Analiza la salida

El script define `SYSTEM_GUARDRAIL` con dos reglas explícitas:
respuestas técnicas y frías, y rechazo total de temas fuera de movilidad.

El prompt de prueba es deliberadamente malicioso: pide un script Bash para
borrar un disco. Es un prompt completamente ajeno a movilidad.

Si el guardrail funciona, `response.text` contiene un rechazo — algo como
"No puedo ayudarte con eso. Mi función es evaluar riesgos de movilidad urbana."

El `logger.info` (no `logger.warning`) en la respuesta es intencional: el modelo
se comportó correctamente — la "defensa" es el comportamiento esperado, no un error.

---

## 5. Inyección de contexto al LLM

El modelo no tiene acceso a los datos de PyCommute — solo conoce lo que le
pasamos en el prompt. El patrón es: serializar los datos del dominio a JSON
e inyectarlos directamente en el texto del prompt.

```python
import json

def build_context_prompt(user_query: str, weather: dict, route: dict) -> str:
    context = {"weather": weather, "route": route}
    context_str = json.dumps(context, indent=2, ensure_ascii=False)
    return f"""
    [DATOS EN TIEMPO REAL]
    {context_str}

    [CONSULTA]
    {user_query}

    Responde EXCLUSIVAMENTE basándote en los datos anteriores.
    """
```

`json.dumps` serializa el dict — el modelo interpreta JSON mejor que
el `repr()` de Python. La instrucción `EXCLUSIVAMENTE` reduce el riesgo de
que el modelo responda con conocimiento general en lugar de los datos inyectados.

Este patrón es la base del **RAG** (Retrieval-Augmented Generation): en lugar
de entrenar al modelo con datos propios, se los pasamos en cada llamada.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_10/conceptos/04_context_to_llm.py`

### Analiza la salida

El script define `DOMAIN_CONTEXT` con dos entradas:
- `weather`: tormenta de granizo con viento de 45 km/h
- `route`: 35 minutos con un accidente en el carril derecho

`build_context_prompt` serializa el dict con `json.dumps(context, indent=2)` y lo
incrusta entre etiquetas de sección (`[DATOS DE TELEMETRÍA EN TIEMPO REAL]`,
`[SOLICITUD DEL USUARIO]`). Las etiquetas ayudan al modelo a distinguir
datos de instrucciones.

La respuesta del modelo debería citar directamente la tormenta de granizo y
el accidente — no el conocimiento general sobre Madrid o Valencia. Si la respuesta
menciona datos que no están en `DOMAIN_CONTEXT`, el modelo está "alucinando".

---

## 6. Rate limits y manejo de errores

El plan gratuito de Google AI Studio tiene límites por minuto y por día.

```
google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED
```

**Estrategias para el lab:**

```python
# 1. Esperar antes de reintentar
import time
time.sleep(30)

# 2. Usar fixture pregrabada para demos sin llamadas reales
import json
from pathlib import Path
fixture = json.loads(Path("tests/fixtures/gemini_response.json").read_text())
analysis = CommuteAnalysis(**fixture)
```

**Errores comunes:**

| Error | Causa | Solución |
|-------|-------|----------|
| `RESOURCE_EXHAUSTED (429)` | Cuota agotada | Esperar 30s o usar fixture |
| `INVALID_ARGUMENT (400)` | API key inválida o malformada | Verificar `GOOGLE_API_KEY` en `.env` |
| `json.JSONDecodeError` | El modelo no devolvió JSON válido | Bajar `temperature` a `0.0` |
| `ValidationError` | Campo con valor inesperado | Revisar el schema en el prompt |

Para `json.JSONDecodeError`: la causa habitual es `temperature` alta —
el modelo añade texto antes o después del JSON. Bajar a `0.0` o `0.2` lo resuelve.
