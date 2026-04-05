"""
Cliente base de Gemini con el SDK google-genai.

Demuestra el patrón mínimo para conectar con la API:
  - Leer GOOGLE_API_KEY del entorno (nunca hardcodeada)
  - Crear genai.Client — un objeto por aplicación
  - Hacer una llamada de prueba con client.models.generate_content
  - Capturar APIError si la conexión falla

Ejecutar (desde curso/):
    uv run python scripts/clase_10/conceptos/01_gemini_basico.py
"""

import os
import sys

from google import genai
from google.genai.errors import APIError
from loguru import logger


def initialize_modern_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.critical("GOOGLE_API_KEY no encontrada en el entorno.")
        sys.exit(1)

    # genai.Client recibe la API key explícitamente — sin estado global
    logger.info("Cliente moderno Gemini inicializado.")
    return genai.Client(api_key=api_key)


if __name__ == "__main__":
    client = initialize_modern_client()
    try:
        logger.debug("Enviando ping al modelo...")
        # client.models.generate_content: punto de entrada unificado para todas las llamadas
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents="Devuelve solo la palabra 'ACK'."
        )
        logger.success(f"Respuesta: {response.text.strip()}")
    except APIError as e:
        # APIError captura errores HTTP de la API (429, 400, 500...)
        logger.error(f"Fallo en la comunicación con la API: {e.message}")
