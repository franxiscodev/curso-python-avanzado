"""anyio.create_task_group(): recolectar resultados de tareas paralelas.

Patron clave: usar un dict compartido para que cada tarea
guarde su resultado. El dict esta disponible al salir del task group.

Ejecutar:
    uv run scripts/clase_05/conceptos/02_anyio_task_group.py
"""

from typing import Any

import anyio


async def fetch_simulado(fuente: str, delay: float) -> dict[str, Any]:
    """Simula una llamada a una API externa con delay configurable."""
    await anyio.sleep(delay)
    return {"fuente": fuente, "dato": f"resultado de {fuente}"}


async def ejemplo_basico() -> None:
    """Patron fundamental: dict compartido para recoger resultados."""
    print("=== Patron basico: dict compartido ===")

    resultados: dict[str, Any] = {}

    async def tarea_clima() -> None:
        resultados["clima"] = await fetch_simulado("OpenWeather", 0.4)

    async def tarea_ruta() -> None:
        resultados["ruta"] = await fetch_simulado("OpenRouteService", 0.3)

    async with anyio.create_task_group() as tg:
        tg.start_soon(tarea_clima)
        tg.start_soon(tarea_ruta)
    # Aqui AMBAS tareas han terminado

    print(f"  Clima: {resultados['clima']}")
    print(f"  Ruta:  {resultados['ruta']}")
    print()


async def ejemplo_multiples_items() -> None:
    """Patron con lista: multiples items en paralelo."""
    print("=== Patron con lista: items en paralelo ===")

    ciudades = ["Madrid", "Valencia", "Barcelona"]
    resultados: list[dict] = []
    lock = anyio.Lock()  # para append seguro desde multiples tareas

    async def fetch_ciudad(ciudad: str) -> None:
        resultado = await fetch_simulado(ciudad, 0.2)
        async with lock:
            resultados.append(resultado)

    async with anyio.create_task_group() as tg:
        for ciudad in ciudades:
            tg.start_soon(fetch_ciudad, ciudad)

    print(f"  {len(resultados)} ciudades consultadas en paralelo:")
    for r in resultados:
        print(f"    {r}")
    print()


async def ejemplo_error_handling() -> None:
    """Error handling: cualquier excepcion cancela el grupo."""
    print("=== Error handling en task group ===")

    async def tarea_ok() -> None:
        await anyio.sleep(0.1)
        print("  tarea_ok: completada")

    async def tarea_falla() -> None:
        await anyio.sleep(0.05)
        raise ValueError("algo salio mal")

    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(tarea_ok)
            tg.start_soon(tarea_falla)
    except* ValueError as eg:
        print(f"  Error capturado: {eg.exceptions[0]}")
        print("  tarea_ok fue cancelada automaticamente")
    print()


anyio.run(ejemplo_basico)
anyio.run(ejemplo_multiples_items)
anyio.run(ejemplo_error_handling)
