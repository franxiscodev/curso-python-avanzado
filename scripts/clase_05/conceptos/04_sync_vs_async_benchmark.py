"""Benchmark: sincronico vs asincrono con peticiones HTTP reales.

Hace N peticiones a httpbin.org/delay/0.3 — un endpoint que tarda
300ms en responder — midiendo el tiempo total en modo sincrono y
asincrono para mostrar el speedup de la concurrencia.

Nota: requiere conexion a internet.

Ejecutar:
    uv run scripts/clase_05/conceptos/04_sync_vs_async_benchmark.py
"""

import time

import anyio
import httpx

URL = "https://httpbin.org/delay/0.3"  # tarda ~300ms por peticion
N = 3


def sync_requests(n: int) -> float:
    """Hace n peticiones de forma sincrona (secuencial)."""
    inicio = time.perf_counter()
    with httpx.Client(timeout=10.0) as client:
        for i in range(n):
            client.get(URL)
            print(f"  sync: peticion {i + 1}/{n} completada")
    return time.perf_counter() - inicio


async def async_requests(n: int) -> float:
    """Hace n peticiones de forma asincrona (paralela)."""
    inicio = time.perf_counter()
    completadas = [0]  # lista para mutacion desde coroutines

    async def fetch(i: int) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.get(URL)
        completadas[0] += 1
        print(f"  async: peticion {i + 1}/{n} completada")

    async with anyio.create_task_group() as tg:
        for i in range(n):
            tg.start_soon(fetch, i)

    return time.perf_counter() - inicio


print(f"Benchmark: {N} peticiones a {URL}")
print(f"(cada peticion tarda ~300ms)\n")

print("--- Sincrono ---")
t_sync = sync_requests(N)
print(f"Tiempo total sincrono: {t_sync:.2f}s\n")

print("--- Asincrono ---")
t_async = anyio.run(async_requests, N)
print(f"Tiempo total asincrono: {t_async:.2f}s\n")

print("--- Resultado ---")
if t_async > 0:
    speedup = t_sync / t_async
    print(f"Speedup: {speedup:.1f}x mas rapido en modo asincrono")
    print(f"Tiempo ahorrado: {t_sync - t_async:.2f}s")
    print()
    print("Por que:")
    print(f"  Sincrono:  {N} x 0.3s = ~{N * 0.3:.1f}s (espera secuencial)")
    print(f"  Asincrono: max(0.3s, 0.3s, ...) = ~0.3s (todas en paralelo)")
