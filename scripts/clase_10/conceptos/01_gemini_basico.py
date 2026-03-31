"""Concepto 1 — Gemini API: primera llamada.

Demuestra:
- Configurar el cliente con google-genai SDK
- generate_content: prompt de texto, respuesta de texto
- Fallback simulado cuando no hay GOOGLE_API_KEY

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_10/conceptos/01_gemini_basico.py

    # Linux
    uv run scripts/clase_10/conceptos/01_gemini_basico.py
"""

import os

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY", "")

if not api_key:
    # Fallback simulado — el script funciona sin API key
    print("GOOGLE_API_KEY no configurada — demo con respuesta simulada")
    print()
    print("Prompt: 'Di Hola desde Gemini en espanol'")
    print("Respuesta simulada: Hola desde Gemini!")
    print()
    print("Para usar la API real, agrega GOOGLE_API_KEY a tu .env")
else:
    from google import genai

    # Cliente unico — recibe la API key en el constructor
    client = genai.Client(api_key=api_key)

    # Llamada basica: prompt de texto → respuesta de texto
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Di 'Hola desde Gemini' en espanol",
    )
    print(f"Respuesta: {response.text}")

# ── Que hace generate_content ────────────────────────────────────────────────
#
# generate_content() es la funcion mas simple de la API:
# - Acepta un string como prompt
# - Devuelve un objeto con .text (la respuesta como string)
# - Es sincrona — para async usa client.aio.models.generate_content()
#
# El modelo "gemini-2.0-flash" es rapido y gratuito hasta cierto limite.
# Para produccion: "gemini-1.5-pro" ofrece mejor calidad.
