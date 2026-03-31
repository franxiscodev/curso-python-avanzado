"""httpx.AsyncClient: cliente HTTP asincrono.

Demuestra la diferencia entre httpx.Client (sincrono)
y httpx.AsyncClient (asincrono), y como hacer peticiones
en paralelo con anyio.create_task_group().

Nota: este script hace peticiones reales a httpbin.org.
Si no hay conexion a internet, fallara con un error de red.

Ejecutar:
    uv run scripts/clase_05/conceptos/03_httpx_async_client.py
"""

import time

import anyio
import httpx


async def fetch_sincrono_simulado() -> None:
    """Muestra el patron sincrono como referencia (usando httpx.Client)."""
    print("=== httpx.Client (sincrono) — referencia ===")
    print("  # Patron sincrono:")
    print("  with httpx.Client() as client:")
    print("      response = client.get(url)  # bloquea hasta recibir respuesta")
    print("      data = response.json()")
    print()


async def peticion_simple() -> None:
    """Una sola peticion asincrona."""
    print("=== httpx.AsyncClient: una peticion ===")
    inicio = time.perf_counter()

    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/json")
        response.raise_for_status()
        data = response.json()

    print(f"  Claves en respuesta: {list(data.keys())}")
    print(f"  Tiempo: {time.perf_counter() - inicio:.2f}s")
    print()


async def peticiones_paralelas() -> None:
    """Dos peticiones en paralelo usando task group."""
    print("=== httpx.AsyncClient: dos peticiones en paralelo ===")
    resultados: dict = {}
    inicio = time.perf_counter()

    async def fetch_a() -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://httpbin.org/get")
            resultados["a"] = list(resp.json().keys())

    async def fetch_b() -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://httpbin.org/ip")
            resultados["b"] = list(resp.json().keys())

    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch_a)
        tg.start_soon(fetch_b)

    print(f"  Peticion A claves: {resultados.get('a')}")
    print(f"  Peticion B claves: {resultados.get('b')}")
    print(f"  Tiempo: {time.perf_counter() - inicio:.2f}s (ambas en paralelo)")
    print()


async def main() -> None:
    await fetch_sincrono_simulado()
    await peticion_simple()
    await peticiones_paralelas()


anyio.run(main)
