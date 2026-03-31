"""
Ejercicios — Clase 05: Concurrencia Estructurada con async/await y anyio
=========================================================================
Tres ejercicios para practicar async, task groups y manejo de errores async.

Ejecutar (desde curso/):
    uv run python scripts/clase_05/ejercicios_clase_05.py

Requisito: autocontenido, sin imports de pycommute.
"""

import time
from typing import Optional

import anyio


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Función async simple con delay simulado
# Implementa `saludar_async` que:
#   - Es una función `async def`
#   - Recibe un nombre (str) y un delay en segundos (float, default 0.1)
#   - Espera el tiempo indicado con `await anyio.sleep(delay)`
#   - Retorna el string "Hola, {nombre}!"
# Pista: repasa "async def y await" en 01_conceptos.md
async def saludar_async(nombre: str, delay: float = 0.1) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — Dos tareas en paralelo con anyio.create_task_group
# Implementa `ejecutar_en_paralelo` que:
#   - Es `async def`
#   - Crea una lista `resultados: list[str] = []`
#   - Usa `async with anyio.create_task_group() as tg:` para lanzar
#     DOS tareas simultáneas que llamen a `_tarea_simulada` con
#     argumentos ("A", 0.05) y ("B", 0.05) respectivamente
#   - Cada tarea debe añadir su resultado a `resultados`
#   - Retorna la lista `resultados` (orden puede variar)
# Pista: repasa "Task Groups" en 01_conceptos.md
#
# Función auxiliar ya implementada:
async def _tarea_simulada(nombre: str, delay: float, resultados: list) -> None:
    """Espera `delay` segundos y añade un string a la lista resultados."""
    await anyio.sleep(delay)
    resultados.append(f"tarea-{nombre}-completa")


async def ejecutar_en_paralelo() -> list[str]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — Función async con retorno de valor y manejo de errores
# Implementa `obtener_dato_seguro` que:
#   - Es `async def`
#   - Recibe `clave: str` y `simular_error: bool = False`
#   - Si simular_error es True, lanza `ValueError(f"Error al obtener {clave}")`
#   - Si no, espera 0.05 segundos y retorna f"dato-{clave}"
#   - La función LLAMADORA debe capturar el ValueError y retornar None en su lugar
#
# Implementa también `llamar_seguro` que:
#   - Es `async def`
#   - Recibe `clave: str` y `simular_error: bool = False`
#   - Llama a `obtener_dato_seguro` en un try/except ValueError
#   - Retorna el resultado o None si hubo error
# Pista: repasa "Manejo de excepciones en código async" en 01_conceptos.md
async def obtener_dato_seguro(clave: str, simular_error: bool = False) -> str:
    pass  # ← reemplazar con tu implementación


async def llamar_seguro(clave: str, simular_error: bool = False) -> Optional[str]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

async def demo() -> None:
    print("=== Ejercicio 1: saludar_async ===")
    inicio = time.perf_counter()
    saludo = await saludar_async("PyCommute", delay=0.05)
    elapsed = time.perf_counter() - inicio
    if saludo is not None:
        print(f"Resultado: {saludo}")
        print(f"Tiempo: {elapsed:.2f}s (esperado ~0.05s)")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 2: ejecutar_en_paralelo ===")
    inicio = time.perf_counter()
    resultados = await ejecutar_en_paralelo()
    elapsed = time.perf_counter() - inicio
    if resultados:
        print(f"Resultados: {sorted(resultados)}")
        print(f"Tiempo: {elapsed:.2f}s (esperado ~0.05s, no ~0.10s)")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 3: llamar_seguro ===")
    dato_ok = await llamar_seguro("ciudad", simular_error=False)
    dato_error = await llamar_seguro("ciudad", simular_error=True)
    if dato_ok is not None or dato_error is not None:
        print(f"Dato exitoso: {dato_ok}")
        print(f"Dato con error: {dato_error}")
    else:
        print("Sin implementar aún.")


if __name__ == "__main__":
    anyio.run(demo)
