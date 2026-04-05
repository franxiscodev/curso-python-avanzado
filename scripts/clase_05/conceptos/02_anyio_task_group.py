"""anyio.create_task_group(): cancelacion en cascada cuando una tarea falla.

Demuestra el comportamiento de structured concurrency ante errores:
- Tres tareas se lanzan en paralelo con duraciones distintas
- La tarea mas rapida (0.5s) lanza RuntimeError antes de que las otras terminen
- El task group cancela automaticamente las tareas que siguen corriendo
- Cada tarea cancelada recibe anyio.get_cancelled_exc_class() — debe re-lanzarlo
- En Python 3.11+, anyio envuelve el RuntimeError en un ExceptionGroup.
  El main() usa `except*` para capturarlo e iterar sobre las excepciones.

Ejecutar:
    uv run scripts/clase_05/conceptos/02_anyio_task_group.py
"""

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
        # CRÍTICO: siempre re-lanzar la excepción de cancelación.
        # Si no se re-lanza, anyio cree que la tarea terminó limpiamente
        # y el mecanismo de structured concurrency se rompe.
        logger.warning(f"-> {nombre} fue cancelado a mitad de vuelo.")
        raise


async def main():
    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(fetch_service, "OpenWeather", 2.0, False)
            tg.start_soon(fetch_service, "OpenRoute", 1.5, False)
            # Este fallará a los 0.5s, forzando la cancelación de los otros dos
            tg.start_soon(fetch_service, "Ollama_Fallback", 0.5, True)
    except* RuntimeError as eg:
        for exc in eg.exceptions:
            logger.error(f"TaskGroup colapsado por: {exc}")

if __name__ == "__main__":
    anyio.run(main)
