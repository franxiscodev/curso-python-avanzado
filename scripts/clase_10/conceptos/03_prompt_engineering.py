"""Concepto 3 — Prompt Engineering para respuestas estructuradas.

Demuestra:
- Como el diseño del prompt afecta la calidad y parsabilidad de la respuesta
- Diferencia entre prompt vago y prompt estructurado
- Reglas para obtener JSON consistente de un LLM
- System instruction vs prompt del usuario

Este script no hace llamadas a la API — solo muestra los patrones.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_10/conceptos/03_prompt_engineering.py

    # Linux
    uv run scripts/clase_10/conceptos/03_prompt_engineering.py
"""

import json

# ── Comparacion: prompt vago vs prompt estructurado ─────────────────────────

print("=" * 60)
print("PROMPT VAGO")
print("=" * 60)
prompt_vago = "Dame info sobre el tiempo en Valencia para ir en bici"
print(f"Prompt: {prompt_vago!r}")
print()
print("Problema: respuesta impredecible — puede ser:")
print("  - Texto libre de 3 parrafos")
print("  - JSON con claves diferentes en cada llamada")
print("  - Respuesta en otro idioma")
print("  - Imposible de parsear sin heuristicas fragiles")

print()
print("=" * 60)
print("PROMPT ESTRUCTURADO")
print("=" * 60)

schema = {
    "recomendacion": "string — consejo principal",
    "perfil_sugerido": "string — cycling-regular | driving-car | foot-walking",
    "confianza": "string — alta | media | baja",
    "llevar": "array de strings — ropa recomendada",
}

prompt_estructurado = f"""Valencia: 13°C, nublado.
Rutas disponibles: bici 22min, coche 5min, caminando 45min.

Responde UNICAMENTE con un JSON valido:
{json.dumps(schema, ensure_ascii=False, indent=2)}

No agregues texto fuera del JSON. Responde en espanol."""

print(f"Prompt:\n{prompt_estructurado}")
print()
print("Resultado: JSON consistente, validable con Pydantic")

# ── Reglas del prompt engineering para JSON ─────────────────────────────────

print()
print("=" * 60)
print("REGLAS PARA PROMPTS ESTRUCTURADOS")
print("=" * 60)
reglas = [
    "1. Contexto especifico — temperatura, condicion, rutas concretas",
    "2. 'UNICAMENTE JSON' — sin texto adicional (no 'aqui esta tu JSON:')",
    "3. Schema con tipos explicitos — no 'string', sino 'uno de: a, b, c'",
    "4. Especificar el idioma — 'Responde en espanol'",
    "5. System instruction para el rol — 'Eres un asistente de movilidad'",
]
for regla in reglas:
    print(f"  {regla}")

# ── System instruction vs prompt ─────────────────────────────────────────────

print()
print("=" * 60)
print("SYSTEM INSTRUCTION vs PROMPT")
print("=" * 60)
print()
print("System instruction (se envia una vez al crear el modelo):")
print("  - Define el ROL: 'Eres un asistente de movilidad experto'")
print("  - Define el FORMATO: 'Responde en espanol y en JSON'")
print("  - Permanece en contexto durante toda la sesion")
print()
print("Prompt del usuario (se envia en cada llamada):")
print("  - Contiene el CONTEXTO especifico: temperaturas, rutas")
print("  - Contiene el SCHEMA de la respuesta esperada")
print("  - Cambia en cada consulta")
print()
print("Separar rol del contexto hace el codigo mas limpio:")
print("  _SYSTEM_PROMPT = constante en el modulo")
print("  _build_prompt() = metodo que construye el prompt con datos reales")
