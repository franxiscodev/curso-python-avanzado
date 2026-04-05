"""
Generadores con yield — procesamiento lazy de rutas paginadas
==============================================================
Compara dos estrategias para consumir 50 páginas de rutas geográficas:
la estrategia "junior" (carga todo en memoria) y la "senior" (yield).

Conceptos que ilustra:
- fetch_all_routes_bad(): acumula 500,000 strings en una lista antes
  de retornar — ocupa varios MB de RAM.
- fetch_all_routes_pro(): usa yield para devolver una ruta a la vez;
  el objeto generador solo ocupa ~120 bytes independientemente del tamaño.
- sys.getsizeof(): mide el tamaño en bytes del objeto Python.
- next(): consume el primer valor del generador sin ejecutar el resto.

Ejecutar:
    uv run python scripts/clase_06/conceptos/02_generadores_yield.py
"""
import sys


def mock_api_page(page: int) -> list[str]:
    """Simula el adaptador HTTPX trayendo una página de 10,000 rutas."""
    return [f"Ruta_Geo_Data_{i}" for i in range(10_000)]


def fetch_all_routes_bad() -> list[str]:
    """Estrategia Junior: Cargar todas las páginas en memoria antes de retornar."""
    all_routes = []
    for page in range(50):  # 50 páginas
        all_routes.extend(mock_api_page(page))
    return all_routes


def fetch_all_routes_pro():
    """Estrategia Senior: Yielding (Pipeline de datos infinito y ligero)."""
    for page in range(50):
        pagina_actual = mock_api_page(page)
        for ruta in pagina_actual:
            yield ruta  # Pausa la función, devuelve el valor, y espera.


# --- PRUEBA DE IMPACTO ---
rutas_memoria = fetch_all_routes_bad()
print(
    f"RAM usada por Lista: {sys.getsizeof(rutas_memoria) / 1024 / 1024:.2f} MB")

rutas_generador = fetch_all_routes_pro()
print(
    f"RAM usada por Generador: {sys.getsizeof(rutas_generador)} bytes (¡Casi cero!)")

# Consumiendo el primer elemento sin cargar el resto
print(f"Primer valor procesado: {next(rutas_generador)}")
