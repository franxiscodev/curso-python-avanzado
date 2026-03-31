"""
Ejercicios — Clase 10: IA en la Nube con Gemini API
=====================================================
Cuatro ejercicios sobre construcción de prompts, parseo de respuestas JSON
y patrones de resiliencia para llamadas a LLMs.

Ejecutar (desde curso/):
    uv run python scripts/clase_10/ejercicios_clase_10.py

Requisito: autocontenido, sin imports de pycommute.
Sin llamadas reales a la API — trabaja con strings simulados.
"""

import json
from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Modelos de datos ya definidos — no modificar
# ---------------------------------------------------------------------------

class ResumenClima(BaseModel):
    """Modelo que representa la respuesta estructurada de la IA."""

    resumen: str
    recomendacion: str


RESPUESTA_JSON_VALIDA = '{"resumen": "Día soleado en Valencia, 28°C.", "recomendacion": "Lleva gafas de sol."}'
RESPUESTA_JSON_INVALIDA = "Lo siento, no puedo procesar esa solicitud en este momento."


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Construir un prompt de sistema estructurado
# Implementa `construir_prompt_clima(ciudad: str, contexto: str) -> str`
# Debe retornar un string multi-línea con f-string que incluya:
#   - Una primera línea con el rol: "Eres un asistente meteorológico experto."
#   - Una línea con el contexto: "Contexto: {contexto}"
#   - Una línea con la pregunta: "¿Cómo es el clima en {ciudad} hoy?"
#   - Una línea indicando el formato: "Responde en JSON con keys: resumen, recomendacion."
# Pista: repasa "Construcción de prompts" en 01_conceptos.md
def construir_prompt_clima(ciudad: str, contexto: str) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — Parsear respuesta JSON a modelo Pydantic
# Implementa `parsear_respuesta(json_str: str) -> Optional[ResumenClima]`
# Debe:
#   - Intentar hacer json.loads(json_str) para obtener un dict
#   - Construir y retornar ResumenClima(**dict_parseado)
#   - Si json.loads lanza json.JSONDecodeError, retornar None
# Pista: repasa "Parseo de respuestas JSON" en 01_conceptos.md
def parsear_respuesta(json_str: str) -> Optional[ResumenClima]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — Seleccionar primera respuesta JSON válida de una lista
# Implementa `primera_valida(respuestas: list[str]) -> Optional[str]`
# Debe:
#   - Iterar sobre la lista de strings
#   - Retornar el primer string que se pueda parsear con json.loads sin error
#   - Si ninguno es válido, retornar None
# Pista: repasa "Resiliencia ante respuestas malformadas" en 01_conceptos.md
def primera_valida(respuestas: list[str]) -> Optional[str]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 4
# ---------------------------------------------------------------------------

# TODO: Ejercicio 4 — Construir prompt few-shot con ejemplos
# Implementa `construir_prompt_fewshot(ejemplos: list[tuple[str, str]], pregunta: str) -> str`
# Debe:
#   - Comenzar con "Ejemplos:\n"
#   - Para cada (q, a) en ejemplos, añadir "P: {q}\nR: {a}\n"
#   - Finalizar con "P: {pregunta}\nR:"
# Ejemplo:
#   ejemplos = [("¿Clima en Madrid?", '{"resumen": "Frío", "recomendacion": "Abrigo"}')]
#   pregunta = "¿Clima en Valencia?"
#   → "Ejemplos:\nP: ¿Clima en Madrid?\nR: {...}\nP: ¿Clima en Valencia?\nR:"
# Pista: repasa "Few-shot prompting" en 01_conceptos.md
def construir_prompt_fewshot(ejemplos: list[tuple[str, str]], pregunta: str) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo — muestra los resultados (no modificar)
# ---------------------------------------------------------------------------

def demo() -> None:
    print("=== Ejercicio 1: construir_prompt_clima ===")
    prompt = construir_prompt_clima(
        ciudad="Valencia",
        contexto="Temperatura actual 28°C, cielo despejado."
    )
    if prompt is not None:
        print(prompt)
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 2: parsear_respuesta ===")
    resultado = parsear_respuesta(RESPUESTA_JSON_VALIDA)
    if resultado is not None:
        print(f"  resumen: {resultado.resumen}")
        print(f"  recomendacion: {resultado.recomendacion}")
    else:
        print("Sin implementar aún.")

    resultado_invalido = parsear_respuesta(RESPUESTA_JSON_INVALIDA)
    print(f"  JSON inválido → None: {resultado_invalido is None}")

    print("\n=== Ejercicio 3: primera_valida ===")
    respuestas = [
        "Esto no es JSON",
        "Tampoco esto",
        '{"resumen": "Lluvioso", "recomendacion": "Lleva paraguas."}',
        '{"otro": "json"}',
    ]
    primera = primera_valida(respuestas)
    if primera is not None:
        print(f"  Primera válida: {primera}")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 4: construir_prompt_fewshot ===")
    ejemplos = [
        ("¿Clima en Madrid?", '{"resumen": "Frío y nublado", "recomendacion": "Lleva abrigo"}'),
        ("¿Clima en Sevilla?", '{"resumen": "Caluroso y soleado", "recomendacion": "Protector solar"}'),
    ]
    prompt_fs = construir_prompt_fewshot(ejemplos, "¿Clima en Valencia?")
    if prompt_fs is not None:
        print(prompt_fs)
    else:
        print("Sin implementar aún.")


if __name__ == "__main__":
    demo()
