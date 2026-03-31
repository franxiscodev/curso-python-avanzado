"""Concepto 2 — Gemini: respuesta JSON estructurada.

Demuestra:
- Pedir JSON en el prompt con schema explicito
- Parsear la respuesta con json.loads()
- Limpiar el markdown si Gemini agrega ```json ... ```
- Fallback simulado cuando no hay GOOGLE_API_KEY

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_10/conceptos/02_gemini_structured_output.py

    # Linux
    uv run scripts/clase_10/conceptos/02_gemini_structured_output.py
"""

import json
import os

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY", "")

# Schema que le pedimos a Gemini — describe la estructura esperada
SCHEMA = {
    "ciudad": "string",
    "temperatura_descripcion": "string",
    "recomendacion": "string",
    "llevar": "array de strings",
}

PROMPT = f"""
Dado que en Valencia hay 13°C y esta nublado,
responde UNICAMENTE con un JSON valido con esta estructura:
{json.dumps(SCHEMA, ensure_ascii=False)}
No agregues texto fuera del JSON.
"""


def clean_json(raw: str) -> str:
    """Elimina el markdown que Gemini agrega a veces (```json ... ```)."""
    clean = raw.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        clean = parts[1] if len(parts) > 1 else clean
        if clean.startswith("json"):
            clean = clean[4:]
    return clean.strip()


if not api_key:
    # Fallback simulado — el script funciona sin API key
    print("GOOGLE_API_KEY no configurada — respuesta simulada:")
    simulada = {
        "ciudad": "Valencia",
        "temperatura_descripcion": "13°C, nublado",
        "recomendacion": "Buen dia para caminar, lleva una chaqueta ligera",
        "llevar": ["chaqueta ligera", "paraguas por si acaso"],
    }
    print(json.dumps(simulada, ensure_ascii=False, indent=2))
else:
    from google import genai

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=PROMPT,
    )

    raw = response.text
    clean = clean_json(raw)
    data = json.loads(clean)

    print("Respuesta parseada:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

# ── El patron que usamos en GeminiAdapter ───────────────────────────────────
#
# 1. Definir el schema como dict Python
# 2. Incluirlo en el prompt con json.dumps()
# 3. Pedir "UNICAMENTE JSON" — sin texto adicional
# 4. Parsear con json.loads() despues de limpiar markdown
# 5. Validar con Pydantic: AIRecommendation(**data)
#
# Si Gemini devuelve un campo inesperado, Pydantic lanza ValidationError
# en la frontera — antes de que el dato invalido entre al sistema.
