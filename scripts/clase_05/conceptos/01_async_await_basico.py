"""async/await basico: secuencial vs paralelo.

Demuestra la diferencia entre ejecutar tareas una tras otra
y ejecutarlas al mismo tiempo con anyio.create_task_group().

Ejecutar:
    uv run scripts/clase_05/conceptos/01_async_await_basico.py
"""

import time

import anyio


async def tarea_lenta(nombre: str, segundos: float) -> str:
    """Simula una tarea que tarda 'segundos' en completarse (E/S simulada)."""
    print(f"  {nombre}: iniciando ({segundos}s)")
    await anyio.sleep(segundos)
    print(f"  {nombre}: completada")
    return f"{nombre} completada en {segundos}s"


async def secuencial() -> None:
    """Ejecuta las tareas una tras otra — total = suma de tiempos."""
    print("=== Ejecucion SECUENCIAL ===")
    inicio = time.perf_counter()

    await tarea_lenta("Tarea A", 0.5)
    await tarea_lenta("Tarea B", 0.3)

    total = time.perf_counter() - inicio
    print(f"Tiempo total: {total:.2f}s (esperado: ~0.80s)\n")


async def paralela() -> None:
    """Ejecuta las tareas en paralelo — total = maximo de tiempos."""
    print("=== Ejecucion PARALELA (create_task_group) ===")
    inicio = time.perf_counter()

    async with anyio.create_task_group() as tg:
        tg.start_soon(tarea_lenta, "Tarea A", 0.5)
        tg.start_soon(tarea_lenta, "Tarea B", 0.3)
    # El bloque async with espera a que AMBAS tareas terminen

    total = time.perf_counter() - inicio
    print(f"Tiempo total: {total:.2f}s (esperado: ~0.50s)")
    print()
    print("La tarea de 0.3s termino ANTES que la de 0.5s — no habia que esperar.")
    print("El task group termina cuando la ULTIMA tarea completa.")


anyio.run(secuencial)
anyio.run(paralela)
