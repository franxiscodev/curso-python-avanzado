import anyio
from loguru import logger


async def fetch_service(nombre: str, latencia: float, fallar: bool = False):
    try:
        logger.info(f"Iniciando {nombre}...")
        await anyio.sleep(latencia)
        if fallar:
            raise RuntimeError(f"¡Caída catastrófica en {nombre}!")
        logger.success(f"{nombre} completado.")
    except anyio.get_cancelled_exc_class():
        logger.warning(f"-> {nombre} fue cancelado a mitad de vuelo.")
        raise


async def main():
    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(fetch_service, "OpenWeather", 2.0, False)
            tg.start_soon(fetch_service, "OpenRoute", 1.5, False)
            # Este fallará a los 0.5s, forzando la cancelación de los otros dos
            tg.start_soon(fetch_service, "Ollama_Fallback", 0.5, True)
    except RuntimeError as e:
        logger.error(f"TaskGroup colapsado por: {e}")

if __name__ == "__main__":
    anyio.run(main)
