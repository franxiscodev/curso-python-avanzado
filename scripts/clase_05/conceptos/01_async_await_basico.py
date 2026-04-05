"""async/await basico: coroutines, await y anyio.sleep().

Demuestra los fundamentos de async/await:
- async def define una coroutine (no la ejecuta hasta que se await-ea)
- await suspende la coroutine actual y cede el control al event loop
- anyio.sleep() es el equivalente async de time.sleep() — no bloquea el loop
- Las dos llamadas en main() son secuenciales: cada await espera a que
  la anterior termine antes de continuar (la concurrencia real viene
  en el script 02 con create_task_group).

Ejecutar:
    uv run scripts/clase_05/conceptos/01_async_await_basico.py
"""

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

    # Secuencial intencional: cada await bloquea main() hasta que termina.
    # El event loop puede correr otras coroutines durante cada await,
    # pero aquí no hay otras — la concurrencia real llega con create_task_group().
    res_cache = await fetch_cache("Valencia")
    logger.success(res_cache)

    res_api = await fetch_api_externa("Madrid")  # main() espera ~2.0s aquí
    logger.success(res_api)

    # Tiempo esperado: ~2.1s (suma de ambos delays) — eso es lo secuencial
    total = time.perf_counter() - inicio
    logger.info(f"Tiempo total: {total:.2f}s")

if __name__ == "__main__":
    anyio.run(main)
