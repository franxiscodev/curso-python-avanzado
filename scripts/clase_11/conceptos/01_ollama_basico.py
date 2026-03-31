"""Ollama basico — conexion y chat con modelo local.

Demuestra:
- Listar modelos disponibles en Ollama
- Llamada basica con ollama.AsyncClient.chat()
- Manejo de Ollama no disponible

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_11/conceptos/01_ollama_basico.py

    # Linux
    uv run scripts/clase_11/conceptos/01_ollama_basico.py

Requiere Ollama corriendo:
    ollama serve
    ollama pull gemma3:1b
"""

import asyncio

import ollama


async def main() -> None:
    client = ollama.AsyncClient()

    # ── Listar modelos disponibles ────────────────────────────────────
    print("=== Modelos disponibles en Ollama ===")
    try:
        models = await client.list()
        if not models.models:
            print("  (sin modelos descargados — ejecuta: ollama pull gemma3:1b)")
        for model in models.models:
            print(f"  {model.model}")
    except Exception as e:
        print(f"  Ollama no esta corriendo: {e}")
        print("  Ejecutar: ollama serve")
        return

    # ── Chat basico ──────────────────────────────────────────────────
    print("\n=== Chat basico con gemma3:1b ===")
    try:
        response = await client.chat(
            model="gemma3:1b",
            messages=[
                {"role": "user", "content": "Di 'Hola desde Ollama' en espanol. Solo eso."},
            ],
        )
        print(f"Respuesta: {response.message.content}")

        # El objeto response tiene metadatos utiles
        print(f"\nMetadatos:")
        print(f"  Modelo: {response.model}")
        print(f"  Tokens de entrada: {response.prompt_eval_count}")
        print(f"  Tokens de salida: {response.eval_count}")
    except ollama.ResponseError as e:
        print(f"  Error de Ollama: {e.error}")
        print("  Verifica que el modelo esta descargado: ollama list")

    # ── System prompt ────────────────────────────────────────────────
    print("\n=== Con system prompt ===")
    try:
        response = await client.chat(
            model="gemma3:1b",
            messages=[
                {"role": "system", "content": "Eres un asistente que responde solo en espanol."},
                {"role": "user", "content": "What is the capital of Spain?"},
            ],
        )
        print(f"Respuesta: {response.message.content}")
    except ollama.ResponseError as e:
        print(f"  Error: {e.error}")


asyncio.run(main())
