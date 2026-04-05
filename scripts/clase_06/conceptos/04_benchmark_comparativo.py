"""
Benchmark comparativo — timeit y la decisión de Pydantic V2
=============================================================
Mide 500,000 repeticiones de dos estrategias de validación de un DTO
de coordenadas: parseo manual en Python puro vs Pydantic V2 (core en Rust).

Conceptos que ilustra:
- timeit.timeit(fn, number=N): repite fn exactamente N veces y retorna
  el tiempo total en segundos. Es más preciso que time.perf_counter para
  microbenchmarks porque minimiza el impacto de la recolección de basura.
- parseo_manual(): convierte y valida campos a mano con float() y str().
- parseo_pydantic(): instancia un modelo BaseModel; el core en Rust valida
  y convierte en una sola operación.
- El resultado muestra que el casting manual es más rápido en datos ya
  correctamente tipados. El valor de Pydantic no está en la velocidad bruta
  sino en la validación automática, los mensajes de error y la coerción de
  tipos desde strings (variables de entorno, JSON de APIs).

Ejecutar:
    uv run python scripts/clase_06/conceptos/04_benchmark_comparativo.py
"""
import timeit
from pydantic import BaseModel

# Nuestro DTO en formato nativo de Python
raw_data = {"lat": 39.4699, "lon": -0.3763, "city": "Valencia"}


class LocationDTO(BaseModel):
    lat: float
    lon: float
    city: str


def parseo_manual():
    # Forma prehistórica de validar tipos
    lat = float(raw_data["lat"])
    lon = float(raw_data["lon"])
    city = str(raw_data["city"])
    return {"lat": lat, "lon": lon, "city": city}


def parseo_pydantic():
    # Validación elegante con core en Rust
    return LocationDTO(**raw_data)


# Configuración del benchmark
REPETICIONES = 500_000

print(f"Iniciando Benchmark: {REPETICIONES} validaciones...")
print("-" * 50)

t_manual = timeit.timeit(parseo_manual, number=REPETICIONES)
print(f"Parseo Manual (Python Puro): {t_manual:.4f} segundos")

t_pydantic = timeit.timeit(parseo_pydantic, number=REPETICIONES)
print(f"Parseo Pydantic V2 (Rust):   {t_pydantic:.4f} segundos")
