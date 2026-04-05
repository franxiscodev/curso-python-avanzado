"""
Resiliencia bajo carga concurrente — benchmark de fallback con anyio.

Demuestra que el patrón fallback funciona correctamente con 10 peticiones en paralelo:
  - flaky_cloud: falla el 60% de las veces (simula throttling de Gemini)
  - reliable_local: nunca falla, pero es 4x más lento (inferencia local)
  - process_request: orquesta el fallback por petición individual
  - run_benchmark: lanza las 10 peticiones con anyio.create_task_group

El reporte final muestra cuántas peticiones se atendieron por cada proveedor
y confirma que el uptime fue del 100% — ninguna petición se perdió.

Ejecutar (desde curso/):
    uv run python scripts/clase_11/conceptos/04_resiliencia_comparativa.py
"""

import random
import time

import anyio
from loguru import logger


class QuotaExceededError(Exception):
    pass


async def flaky_cloud(req_id: int) -> str:
    """Simula una API Cloud inestable que corta conexiones por Throttling."""
    await anyio.sleep(0.2)  # Latencia baja: la nube responde rápido cuando funciona
    # 60% de fallos simula un escenario de throttling por concurrencia elevada
    if random.random() < 0.60:
        logger.debug(f"[Req {req_id}] NUBE: Error 429 Too Many Requests")
        raise QuotaExceededError("Throttling en API Cloud")

    logger.success(f"[Req {req_id}] NUBE: Respuesta exitosa")
    return "Cloud_Data"


async def reliable_local(req_id: int) -> str:
    """Simula nuestro modelo local. Nunca falla, pero es más lento."""
    await anyio.sleep(0.8)  # Latencia mayor: inferencia en CPU local es más costosa
    logger.info(f"[Req {req_id}] LOCAL: Fallback exitoso")
    return "Local_Data"


async def process_request(req_id: int, results: list):
    """Orquestador por petición: intenta cloud, cae a local si falla."""
    start_time = time.perf_counter()
    try:
        source = await flaky_cloud(req_id)
    except QuotaExceededError:
        source = await reliable_local(req_id)  # fallback transparente

    elapsed = time.perf_counter() - start_time
    results.append((req_id, source, elapsed))


async def run_benchmark():
    logger.info("=== INICIANDO BENCHMARK CONCURRENTE ===")
    results = []

    # create_task_group lanza las 10 peticiones en paralelo — concurrencia estructurada
    async with anyio.create_task_group() as tg:
        for i in range(1, 11):
            tg.start_soon(process_request, i, results)

    # Análisis de métricas al finalizar las 10 peticiones
    cloud_count = sum(1 for r in results if r[1] == "Cloud_Data")
    local_count = sum(1 for r in results if r[1] == "Local_Data")

    logger.warning("=== REPORTE DE RESILIENCIA ===")
    logger.info(f"Total procesadas : {len(results)}/10 (100% Uptime)")
    logger.info(f"Atendidas x Nube : {cloud_count} (Rapidas)")
    logger.info(f"Atendidas x Local: {local_count} (Salvadas por Fallback)")


if __name__ == "__main__":
    anyio.run(run_benchmark)
