"""Ollama con salida estructurada — JSON desde modelo local.

Demuestra:
- Pedir JSON estructurado a un modelo local
- Limpiar markdown que el modelo puede agregar (```json...```)
- Validar la respuesta con un schema manual

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_11/conceptos/02_ollama_structured.py

    # Linux
    uv run scripts/clase_11/conceptos/02_ollama_structured.py

Nota: modelos pequenos como gemma3:1b pueden no seguir el schema al 100%.
Si la respuesta no es JSON valido, reintentar o usar modelo mas grande.
"""

import asyncio
import json

import ollama

PROMPT = """Dado que en Valencia hay 13C y cielo despejado, y en Madrid hay 3C y cielo claro:

Responde UNICAMENTE con un JSON valido con esta estructura exacta:
{
  "ciudad_origen": "string",
  "ciudad_destino": "string",
  "recomendacion": "string — consejo de viaje",
  "llevar": ["item1", "item2", "item3"]
}

No agregues texto ni explicaciones fuera del JSON."""


def clean_json(raw: str) -> str:
    """Elimina el markdown que el modelo agrega a veces (```json...```)."""
    clean = raw.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        clean = parts[1] if len(parts) > 1 else clean
        if clean.startswith("json"):
            clean = clean[4:]
    return clean.strip()


async def main() -> None:
    client = ollama.AsyncClient()

    print("=== Ollama con respuesta JSON estructurada ===")
    print(f"Prompt enviado:\n{PROMPT}\n")

    try:
        response = await client.chat(
            model="gemma3:1b",
            messages=[{"role": "user", "content": PROMPT}],
        )

        raw = response.message.content
        print(f"Respuesta cruda:\n{raw}\n")

        clean = clean_json(raw)
        print(f"JSON limpio:\n{clean}\n")

        data = json.loads(clean)
        print("=== Datos parseados ===")
        print(f"  Origen:        {data.get('ciudad_origen', '?')}")
        print(f"  Destino:       {data.get('ciudad_destino', '?')}")
        print(f"  Recomendacion: {data.get('recomendacion', '?')}")
        print(f"  Llevar:        {', '.join(data.get('llevar', []))}")

    except json.JSONDecodeError as e:
        print(f"  La respuesta no es JSON valido: {e}")
        print("  Tip: modelos pequenos a veces ignoran el schema.")
        print("       Prueba con un prompt mas restrictivo o un modelo mas grande.")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Verifica que Ollama esta corriendo: ollama serve")


asyncio.run(main())
