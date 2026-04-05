"""
Salida estructurada de Ollama con validación Pydantic V2.

Demuestra el pipeline completo: prompt con schema explícito → JSON de Ollama → BaseModel:
  - WeatherAdvice define el contrato (qué campos esperamos)
  - format="json" en el payload instruye a Ollama a devolver JSON sin markdown
  - model_validate_json valida el string de respuesta en un solo paso
  - ValidationError captura el caso de "el modelo alucinó" con un campo incorrecto

La combinación de format="json" + Pydantic es equivalente a lo que hace
response_schema en el SDK de Gemini (Clase 10) — mismo patrón, distinta API.

Ejecutar (desde curso/):
    uv run python scripts/clase_11/conceptos/02_ollama_structured.py
"""

import anyio
import httpx
from loguru import logger
from pydantic import BaseModel, Field, ValidationError


# El contrato define exactamente qué campos y tipos esperamos del modelo
class WeatherAdvice(BaseModel):
    risk_level: str = Field(description="Nivel de riesgo: 'Bajo', 'Medio' o 'Alto'")
    actionable_tip: str = Field(
        description="Consejo práctico de conducción de máximo 15 palabras"
    )


async def get_structured_advice(weather_condition: str) -> WeatherAdvice:
    logger.info(f"Solicitando consejo para clima: {weather_condition}")

    # El prompt pide JSON explícitamente con los nombres de campo del contrato
    prompt = f"""
    Genera un consejo de conducción para clima: {weather_condition}.
    Responde estrictamente en JSON usando las llaves 'risk_level' y 'actionable_tip'.
    """

    async with httpx.AsyncClient(timeout=45.0) as client:
        res = await client.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "format": "json",   # Ollama fuerza JSON sin bloques markdown
                "stream": False,
            },
        )
        res.raise_for_status()
        raw_json = res.json()["response"]  # string JSON devuelto por Ollama

        # model_validate_json: parsea el string y valida tipos en un paso
        # Si risk_level llega como "Extremo" (no en el contrato), lanza ValidationError
        try:
            validated_data = WeatherAdvice.model_validate_json(raw_json)
            return validated_data
        except ValidationError as e:
            logger.error(f"La IA alucinó y rompió el contrato JSON: {e}")
            raise


if __name__ == "__main__":
    try:
        advice = anyio.run(get_structured_advice, "Lluvia torrencial y granizo")
        print(f"\n[RIESGO]: {advice.risk_level.upper()}")
        print(f"[CONSEJO]: {advice.actionable_tip}")
    except Exception:
        print("Fallo en la extracción de datos.")
