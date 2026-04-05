"""
Concepto 4: Concurrencia estructurada dentro de endpoints FastAPI.

anyio.create_task_group() dentro de un endpoint async permite ejecutar
varias operaciones I/O en paralelo sin salir del flujo normal:
- fetch_weather (1s) y fetch_route (2s) se lanzan simultáneamente.
- El bloque 'async with' espera a que AMBAS terminen.
- Tiempo total: ~2s (el más lento), no 3s (suma secuencial).

Concurrencia estructurada garantiza:
- Si una tarea lanza excepción, la otra se cancela automáticamente.
- No hay tareas huérfanas — el grupo limpia al salir del bloque.
- El dict 'results' se comparte de forma segura porque anyio es
  single-threaded (no hay condiciones de carrera en CPython).

Aplicar este patrón cuando el endpoint necesita varias fuentes de datos
independientes (weather + route, precio + disponibilidad, etc.).

Ejecutar:
  uv run uvicorn scripts.clase_12.conceptos.04_async_endpoints:app --reload
  curl "http://localhost:8000/dashboard?origin=Valencia&dest=Madrid"
"""

import time

import anyio
from fastapi import FastAPI

app = FastAPI()


async def fetch_weather(city: str, results: dict):
    await anyio.sleep(1.0)  # Simula I/O de red
    results["weather"] = f"Soleado en {city}"


async def fetch_route(origin: str, dest: str, results: dict):
    await anyio.sleep(2.0)  # Simula I/O de red
    results["route"] = f"Ruta óptima de {origin} a {dest}"


@app.get("/dashboard")
async def get_dashboard(origin: str = "Valencia", dest: str = "Madrid"):
    start_time = time.time()
    results = {}

    # Concurrencia estructurada: Si una tarea falla, se cancela la otra automáticamente.
    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch_weather, origin, results)
        tg.start_soon(fetch_route, origin, dest, results)

    # El bloque 'with' asegura que ambas tareas terminaron aquí
    elapsed = time.time() - start_time

    return {
        "data": results,
        "processing_time": f"{elapsed:.2f}s",  # Esto tomará ~2.0s, no 3.0s!
    }
