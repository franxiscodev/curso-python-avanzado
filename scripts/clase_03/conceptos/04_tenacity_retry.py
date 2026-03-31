"""Demo Tenacity @retry — Clase 3, Concepto 4.

@retry añade resiliencia ante fallos transitorios sin modificar
la lógica de la función. La función no sabe que está siendo reintentada.

Nota: wait_fixed(1) espera 1 segundo entre intentos.
Este script tarda ~2 segundos en ejecutarse (2 reintentos x 1s).

Ejecuta este script con:
    uv run scripts/clase_03/conceptos/04_tenacity_retry.py
"""

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

intento = 0


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
)
def operacion_inestable() -> str:
    global intento
    intento += 1
    logger.info("Intento {n} de 3", n=intento)
    if intento < 3:
        raise ConnectionError(f"Fallo simulado en intento {intento}")
    return "Exito en intento 3"


resultado = operacion_inestable()
print(f"\nResultado: {resultado}")
