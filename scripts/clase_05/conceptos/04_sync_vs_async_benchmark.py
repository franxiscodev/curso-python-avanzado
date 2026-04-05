"""Benchmark: sincronico vs asincrono con peticiones HTTP reales.

Hace N peticiones a httpbin.org/delay/1 — un endpoint que tarda
1 segundo en responder — midiendo el tiempo total en modo sincrono y
asincrono para mostrar el speedup de la concurrencia:

  Sincrono (secuencial): PETICIONES * 1s  → ~5s para 5 peticiones
  Asincrono (paralelo):  ~1s sin importar cuantas peticiones haya

Nota: requiere conexion a internet.

Ejecutar:
    uv run scripts/clase_05/conceptos/04_sync_vs_async_benchmark.py
"""

import time
import httpx
import anyio
from loguru import logger

URL = "https://httpbin.org/delay/1"
PETICIONES = 5


def run_sync():
    logger.warning("Iniciando modo SÍNCRONO (Bloqueante)...")
    start = time.perf_counter()
    with httpx.Client() as client:
        for i in range(PETICIONES):
            client.get(URL)
            logger.info(f"Síncrono: Petición {i+1} completada.")
    total = time.perf_counter() - start
    logger.error(f"Tiempo total Síncrono: {total:.2f} segundos")


async def fetch(client: httpx.AsyncClient, i: int):
    await client.get(URL)
    logger.info(f"Asíncrono: Petición {i+1} completada.")


async def run_async():
    logger.success("Iniciando modo ASÍNCRONO (Concurrente)...")
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        async with anyio.create_task_group() as tg:
            for i in range(PETICIONES):
                tg.start_soon(fetch, client, i)
    total = time.perf_counter() - start
    logger.success(f"Tiempo total Asíncrono: {total:.2f} segundos")

if __name__ == "__main__":
    # Removemos el handler por defecto de loguru para limpiar el output visual
    import sys
    logger.remove()
    logger.add(sys.stderr, format="<level>{message}</level>")

    run_sync()
    print("-" * 40)
    anyio.run(run_async)
