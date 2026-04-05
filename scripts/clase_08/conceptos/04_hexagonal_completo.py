"""
Concepto 4: Arquitectura Hexagonal completa con Pydantic V2.

Muestra los cuatro componentes de la arquitectura juntos:

  1. Entidad de dominio — CommuteResult (Pydantic BaseModel):
     Contrato estricto de salida. AdviseService siempre devuelve
     este tipo validado, nunca un dict libre.

  2. Puerto — AIProviderPort (Protocol):
     El Core solo conoce este contrato. No sabe si hay Gemini,
     Ollama, un mock o cualquier otra cosa detrás.

  3. Servicio — AdviseService (Core):
     Recibe AIProviderPort por constructor. Orquesta la lógica:
     construye el contexto, llama al proveedor, devuelve CommuteResult.

  4. Adaptadores — GeminiAdapter / OllamaAdapter:
     Ambos implementan AIProviderPort sin herencia.
     "Cambiar de Gemini a Ollama es cambiar una línea" en el ensamblador:
       ai_client = GeminiAdapter()   # produccion
       ai_client = OllamaAdapter()   # fallback local

Conexión con el proyecto:
  En Clase 10 añadimos GeminiAdapter real. En Clase 11 añadimos
  OllamaAdapter real. En Clase 11 también aparece FallbackAIAdapter
  que usa ambos — posible gracias a que los dos implementan AIProviderPort.
  CommuteResult aquí anticipa el contrato que Pydantic V2 formalizará
  en Clase 09.

Ejecutar:
  uv run python scripts/clase_08/conceptos/04_hexagonal_completo.py
"""

from typing import Protocol

from pydantic import BaseModel, Field


# 1. ENTIDADES / MODELOS DE DOMINIO (Pydantic V2)
class CommuteResult(BaseModel):
    origin: str
    destination: str
    ai_recommendation: str = Field(..., description="Consejo de la IA")
    is_safe: bool = Field(default=True)


# 2. PUERTOS (Interfaces)
class AIProviderPort(Protocol):
    def get_advice(self, context: str) -> str: ...


# 3. CORE (Lógica de Negocio)
class AdviseService:
    def __init__(self, ai_provider: AIProviderPort):
        self.ai = ai_provider

    def analyze_route(self, origin: str, dest: str) -> CommuteResult:
        context = f"Ruta desde {origin} hasta {dest} con tráfico moderado."

        # El Core orquesta, no implementa
        advice = self.ai.get_advice(context)

        # Retornamos un contrato estricto gracias a Pydantic
        return CommuteResult(
            origin=origin,
            destination=dest,
            ai_recommendation=advice,
            is_safe="peligro" not in advice.lower(),
        )


# 4. ADAPTADORES (Infraestructura)
class GeminiAdapter:
    def get_advice(self, context: str) -> str:
        # Aquí iría la llamada real usando google-genai
        return f"[Gemini 2.5 Flash] Sugiere salir 10 mins antes. Contexto: {context}"


class OllamaAdapter:
    def get_advice(self, context: str) -> str:
        # Fallback local
        return f"[Gemma Local] Ruta despejada. Contexto: {context}"


# 5. MAIN / APP (Ensamblaje)
if __name__ == "__main__":
    # Cambiar de Gemini a Ollama es literalmente cambiar una línea aquí
    ai_client = GeminiAdapter()
    service = AdviseService(ai_provider=ai_client)

    result = service.analyze_route("Valencia", "Madrid")

    print("=== Resultado Validado por Pydantic ===")
    print(result.model_dump_json(indent=2))
