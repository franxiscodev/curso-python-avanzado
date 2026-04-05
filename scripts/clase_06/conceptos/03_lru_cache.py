"""
lru_cache — Evitar llamadas repetidas a la API del clima
=========================================================
Demuestra el patrón de memoización con @lru_cache: la primera petición
por ciudad hace la llamada simulada (1.5s); las siguientes son instantáneas
porque el resultado se sirve desde cache en memoria.

Conceptos que ilustra:
- @lru_cache(maxsize=128): decora obtener_clima_openweather; retiene los
  resultados de las últimas 128 ciudades distintas (LRU eviction).
- Cache hit vs cache miss: Madrid se consulta dos veces, la segunda es gratis.
- cache_info(): expone hits, misses, maxsize y currsize del cache interno.
- time.perf_counter(): mide el tiempo real de cada llamada para evidenciar
  el ahorro del hit.

Ejecutar:
    uv run python scripts/clase_06/conceptos/03_lru_cache.py
"""
import time
from functools import lru_cache


@lru_cache(maxsize=128)
def obtener_clima_openweather(ciudad: str) -> str:
    """
    Adaptador de OpenWeather.
    maxsize=128 retendra las ultimas 128 ciudades diferentes en memoria.
    """
    print(f"[HTTP] Consultando API para {ciudad}...")
    time.sleep(1.5)  # Simulamos latencia de red
    return f"Clima actual en {ciudad}: Soleado, 24 grados"


print("--- Flujo de Usuarios en PyCommute ---")

start = time.perf_counter()
print("Usuario 1 pide:", obtener_clima_openweather("Madrid"))
print(f"Tiempo: {time.perf_counter() - start:.4f}s\n")

start = time.perf_counter()
print("Usuario 2 pide:", obtener_clima_openweather("Valencia"))
print(f"Tiempo: {time.perf_counter() - start:.4f}s\n")

start = time.perf_counter()
# Aqui ocurre la magia. Misma entrada = respuesta instantanea sin red.
print("Usuario 3 pide:", obtener_clima_openweather("Madrid"))
print(f"Tiempo: {time.perf_counter() - start:.4f}s (CACHE HIT)\n")

print("Metricas del Sistema de Cache:")
print(obtener_clima_openweather.cache_info())
