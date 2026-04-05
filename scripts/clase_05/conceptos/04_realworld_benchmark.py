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
