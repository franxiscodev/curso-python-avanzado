"""Demo Tenacity + HTTPX Real — Clase 3, Concepto 4 (Nivel Producción).

Ejecuta este script con:
    uv run python scripts/clase_03/conceptos/05_tenacity_loguru_httpx.py
"""

import sys

import httpx
from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# 1. Configuración de Loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss.SS}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
)


def log_reintento(retry_state):
    """Callback hook. Tenacity nos pasa su estado interno antes de pausar."""
    espera = retry_state.next_action.sleep
    intento = retry_state.attempt_number
    logger.warning(
        f"!!! Timeout en la red. Pausando hilo {espera}s antes del intento {intento + 1}..."
    )


# 2. Tenacity
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.TimeoutException),
    before_sleep=log_reintento,
    reraise=True,  # Relanza la excepción original
)
def llamar_api_lenta():
    logger.info("Petición HTTP (Server tardará 5s, nuestro límite son 2s)")

    # 3. HTTPX con Timeout Estricto.
    with httpx.Client(timeout=2.0) as client:
        # httpbin.org/delay/5 retiene la conexión 5 segundos deliberadamente.
        respuesta = client.get("https://httpbin.org/delay/5")

        # Si por milagro responde, validamos que sea un status 200 OK
        respuesta.raise_for_status()
        return respuesta.json()


if __name__ == "__main__":
    try:
        resultado = llamar_api_lenta()
        logger.success("✅ Datos obtenidos:", resultado)
    except httpx.TimeoutException:
        logger.error(
            "❌ El servidor remoto está inaccesible. Hemos abortado la operación de forma segura tras 3 intentos."
        )
