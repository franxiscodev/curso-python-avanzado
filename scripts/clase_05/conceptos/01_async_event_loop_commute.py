import anyio
import time
from loguru import logger


async def fetch_cache(ciudad: str) -> str:
    logger.info(f"[{ciudad}] Buscando en caché local...")
    await anyio.sleep(0.1)  # Simula latencia de Redis (I/O muy rápido)
    return f"Caché hit para {ciudad}"


async def fetch_api_externa(ciudad: str) -> str:
    logger.info(f"[{ciudad}] Consultando API externa (lento)...")
    await anyio.sleep(2.0)  # Simula latencia de red (I/O lento)
    return f"Datos en vivo de {ciudad}"


async def main():
    inicio = time.perf_counter()

    # Secuencial intencional para demostrar el 'await'
    res_cache = await fetch_cache("Valencia")
    logger.success(res_cache)

    res_api = await fetch_api_externa("Madrid")
    logger.success(res_api)

    total = time.perf_counter() - inicio
    logger.info(f"Tiempo total: {total:.2f}s")

if __name__ == "__main__":
    anyio.run(main)
