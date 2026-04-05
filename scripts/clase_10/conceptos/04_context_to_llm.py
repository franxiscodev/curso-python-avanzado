"""
Inyección de contexto al LLM — el patrón RAG básico con google-genai.

Demuestra cómo pasar datos del dominio directamente en el prompt:
  - DOMAIN_CONTEXT simula la telemetría real de PyCommute (clima + ruta)
  - build_context_prompt serializa el dict a JSON y lo incrusta en el prompt
  - El modelo razona EXCLUSIVAMENTE sobre los datos inyectados, no sobre
    conocimiento general — esto es la base del patrón RAG (Retrieval-Augmented Generation)

La clave es separar "qué sabe el modelo" de "qué le decimos nosotros":
los datos de OpenWeather y ORS se inyectan en el prompt, el modelo solo interpreta.

Ejecutar (desde curso/):
    uv run python scripts/clase_10/conceptos/04_context_to_llm.py
"""

import json
import os

from dotenv import load_dotenv
from google import genai
from loguru import logger

# Simula los datos que PyCommute obtendría de OpenWeather y ORS en producción
DOMAIN_CONTEXT = {
    "weather": {"condition": "Tormenta Granizo", "wind_kmh": 45},
    "route": {"duration_mins": 35, "incidents": ["Accidente en carril derecho"]},
}


def build_context_prompt(user_query: str, context: dict) -> str:
    # json.dumps serializa el dict a string — el modelo lee JSON mejor que repr()
    context_str = json.dumps(context, indent=2)
    return f"""
    [DATOS DE TELEMETRÍA EN TIEMPO REAL]
    {context_str}

    [SOLICITUD DEL USUARIO]
    {user_query}

    Basado EXCLUSIVAMENTE en la telemetría, responde la solicitud.
    """


if __name__ == "__main__":
    load_dotenv()  # Carga las variables del archivo .env
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    final_prompt = build_context_prompt(
        "¿Debería tomar la bicicleta ahora mismo?", DOMAIN_CONTEXT
    )

    logger.debug("Enviando telemetría al modelo gemini-2.5-flash...")
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=final_prompt
    )
    # La respuesta cita los datos inyectados — no inventa información externa
    logger.success(f"Análisis:\n{response.text.strip()}")
