# Clase 10 — IA Cloud con Gemini API

## 1. ¿Qué es un LLM?

Un **Large Language Model** es un modelo de machine learning entrenado para
predecir el siguiente token dado un contexto. No "entiende" — predice con
una probabilidad muy alta de ser coherente con el texto anterior.

**Tokens**: la unidad básica de procesamiento. Aproximadamente 4 caracteres
en inglés, 3-4 en español. "Valencia" = 2 tokens.

**Ventana de contexto**: el límite de tokens que el modelo puede considerar
al mismo tiempo. Gemini 2.0 Flash: 1 millón de tokens — suficiente para
documentos completos o conversaciones largas.

**Temperature**: controla la aleatoriedad de las respuestas.
- `0.0` — determinístico, siempre el token más probable
- `1.0` — balance entre coherencia y variedad
- `2.0` — muy creativo, impredecible

Para respuestas estructuradas (JSON), usar `temperature=0.0` o `0.2`.

---

## 2. Gemini API — primeros pasos

Google ofrece Gemini vía API con el SDK `google-genai`:

```python
from google import genai
from google.genai import types

# Un cliente por aplicación — recibe la API key
client = genai.Client(api_key="tu-api-key")

# Llamada básica
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Di 'Hola' en español",
)
print(response.text)  # "Hola"
```

**System instruction** — define el rol del modelo para toda la sesión:
```python
config = types.GenerateContentConfig(
    system_instruction="Eres un asistente de movilidad experto.",
)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="¿Debería ir en bici con lluvia?",
    config=config,
)
```

**Async** — para no bloquear mientras esperas la respuesta:
```python
response = await client.aio.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=config,
)
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_10/conceptos/01_gemini_basico.py`

---

## 3. Prompt Engineering básico

El prompt es la instrucción que le das al modelo. Su diseño determina
la calidad y consistencia de la respuesta.

**Principios para prompts efectivos:**

```
1. Contexto específico: temperatura, condición, rutas concretas
2. Rol claro: "Eres un experto en X"
3. Formato explícito: "Responde en JSON"
4. Idioma: "Responde en español"
5. Ejemplos (few-shot): incluir input/output de ejemplo si el modelo falla
```

**Ejemplo: prompt vago vs prompt estructurado**

```
Vago: "Dame info sobre Valencia para ir al trabajo"
↓
Respuesta impredecible, difícil de parsear

Estructurado: "Valencia: 13°C, nublado. Responde ÚNICAMENTE con:
               {recomendacion: str, llevar: list[str]}"
↓
JSON predecible, validable con Pydantic
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_10/conceptos/03_prompt_engineering.py`

---

## 4. Respuestas estructuradas — pedir JSON

Para integrar la respuesta del LLM con Pydantic, necesitamos JSON:

```python
import json

# Schema que le pedimos al modelo
schema = {
    "recommendation": "string — consejo principal",
    "suggested_profile": "cycling-regular | driving-car | foot-walking",
    "confidence": "alta | media | baja",
    "outfit_tips": "array de strings — ropa recomendada",
}

prompt = f"""
Valencia: 13°C, nublado. Rutas: bici 22min, coche 5min.

Responde ÚNICAMENTE con un JSON válido con esta estructura:
{json.dumps(schema, ensure_ascii=False, indent=2)}

No agregues explicaciones fuera del JSON.
"""
```

**Limpiar markdown** — Gemini a veces agrega ` ```json ... ``` `:
```python
def clean_json(raw: str) -> str:
    clean = raw.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        clean = parts[1] if len(parts) > 1 else clean
        if clean.startswith("json"):
            clean = clean[4:]
    return clean.strip()

data = json.loads(clean_json(response.text))
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_10/conceptos/02_gemini_structured_output.py`

---

## 5. Del JSON al modelo Pydantic

El pipeline completo desde el prompt hasta el objeto tipado:

```python
from pydantic import BaseModel, Field, field_validator

class Recomendacion(BaseModel):
    recommendation: str = Field(min_length=10)
    suggested_profile: str
    confidence: str

    @field_validator("confidence")
    @classmethod
    def confidence_valid(cls, v: str) -> str:
        valid = {"alta", "media", "baja"}
        if v.lower() not in valid:
            raise ValueError(f"Valor inválido: '{v}'")
        return v.lower()
```

```python
# Llamada a Gemini
response = await client.aio.models.generate_content(
    model="gemini-2.0-flash", contents=prompt, config=config
)

# Parsear y validar
data = json.loads(clean_json(response.text))
rec = Recomendacion(**data)
# Si Gemini devuelve confidence="very-high" → ValidationError aquí
# No en el servicio. No en el frontend. En la frontera.
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_10/conceptos/04_context_to_llm.py`

---

## 6. Rate limits y manejo de errores

El plan gratuito de Google AI Studio tiene límites por minuto y por día.
Si los superas:

```
google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED
```

**Estrategias:**

```python
# 1. Esperar antes de reintentar
import time
time.sleep(30)

# 2. Tener una respuesta pregrabada para tests y demos
import json
from pathlib import Path
fixture = json.loads(Path("fixtures/gemini_response.json").read_text())
rec = AIRecommendation(**fixture)

# 3. Fallback a modelo local (Clase 11)
# OllamaAdapter implementa el mismo AIPort
```

**Otros errores comunes:**

| Error | Causa |
|-------|-------|
| `INVALID_ARGUMENT (400)` | API key inválida o malformada |
| `json.JSONDecodeError` | El modelo no devolvió JSON válido |
| `ValidationError` | Gemini devolvió un campo con valor inesperado |

Para `json.JSONDecodeError`: bajar la temperature a `0.0` o `0.2` suele resolverlo.
