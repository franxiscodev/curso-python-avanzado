"""
Salida estructurada nativa con google-genai y Pydantic V2.

Demuestra cómo pedirle a Gemini que devuelva JSON válido conforme a un schema:
  - Definir el contrato con BaseModel + Field (constraints incluidos)
  - Pasar response_schema=CommuteAnalysis en GenerateContentConfig
  - Validar la respuesta con model_validate_json en un solo paso

El SDK acepta la clase BaseModel directamente como schema — no hace falta
convertirla manualmente a JSON Schema.

Ejecutar (desde curso/):
    uv run python scripts/clase_10/conceptos/02_gemini_structured_output.py
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from loguru import logger
from pydantic import BaseModel, Field


class CommuteAnalysis(BaseModel):
    recommended_mode: str = Field(
        ..., description="Modo de transporte (ej. METRO, BICI)"
    )
    risk_level: int = Field(..., ge=1, le=5, description="Nivel de riesgo del 1 al 5")
    reasoning: str = Field(..., description="Explicación técnica breve")


if __name__ == "__main__":
    load_dotenv()  # Carga las variables del archivo .env
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = "Evalúa ir en moto por Madrid con lluvia intensa."

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                # El SDK acepta la clase BaseModel directamente — sin conversión manual
                response_schema=CommuteAnalysis,
            ),
        )

        # model_validate_json: parsea el string JSON y valida los tipos en un paso
        analysis = CommuteAnalysis.model_validate_json(response.text)
        logger.success(
            f"Modo: {analysis.recommended_mode} | Riesgo: {analysis.risk_level}"
        )

    except Exception as e:
        logger.error(f"Fallo de validación o red: {e}")
