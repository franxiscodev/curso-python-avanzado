"""
Patrón Fallback con reintentos usando tenacity.

Demuestra el flujo completo: intentar cloud → reintentar N veces → fallback a local:
  - QuotaExceededError modela el fallo específico de Gemini (HTTP 429)
  - @retry con reraise=True propaga la excepción original tras agotar los intentos
  - orchestrate_ai captura QuotaExceededError y conmuta al proveedor local

La clave es reraise=True: sin él, tenacity lanza RetryError en lugar de la
excepción original, y el except QuotaExceededError del orquestador no la captura.

Ejecutar (desde curso/):
    uv run python scripts/clase_11/conceptos/03_patron_fallback.py
"""

import anyio
from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class QuotaExceededError(Exception):
    pass


async def primary_cloud_ai(prompt: str) -> str:
    """Simula nuestro proveedor Cloud (Gemini) fallando por cuota."""
    logger.debug("[CLOUD] Conectando a la Nube...")
    raise QuotaExceededError("HTTP 429: Cuota diaria agotada en Gemini API.")


async def fallback_local_ai(prompt: str) -> str:
    """Simula nuestro proveedor Local (Ollama)."""
    logger.info("[LOCAL] Atendiendo petición desde el hardware local.")
    return "CONSEJO LOCAL: Mantén la distancia de seguridad (Generado por gemma3:1b)."


# reraise=True: tras stop_after_attempt(2), propaga QuotaExceededError — no RetryError
@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=5),
    retry=retry_if_exception_type(QuotaExceededError),
    reraise=True,
)
async def try_cloud_with_retries(prompt: str):
    return await primary_cloud_ai(prompt)


async def orchestrate_ai(prompt: str) -> str:
    """Orquesta los intentos al proveedor cloud y el desvío al local."""
    try:
        return await try_cloud_with_retries(prompt)
    except QuotaExceededError as e:
        # Fallback: el cloud falló definitivamente tras los reintentos
        logger.warning(f"Fallback Activado: La nube falló definitivamente. Motivo: {e}")
        return await fallback_local_ai(prompt)


if __name__ == "__main__":
    logger.info("Iniciando solicitud al sistema de IA...")
    result = anyio.run(orchestrate_ai, "Consejos para conducir con niebla.")
    print(f"\nResultado Final: {result}")
