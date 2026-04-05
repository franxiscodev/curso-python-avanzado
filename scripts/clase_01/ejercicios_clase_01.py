"""
Ejercicios — Clase 01: El Setup Profesional
============================================
Tres ejercicios para practicar type hints, variables de entorno
y parseo de respuestas JSON.

Ejecutar:
    uv run python scripts/clase_01/ejercicios_clase_01.py

Requisito: no importa nada de pycommute — es autocontenido.
"""

import json
import os
from typing import Optional


# ---------------------------------------------------------------------------
# Utilidades ya implementadas — no modificar
# ---------------------------------------------------------------------------

RESPUESTA_API_SIMULADA: dict = {
    "name": "Valencia",
    "main": {"temp": 22.5, "feels_like": 21.0, "humidity": 65},
    "weather": [{"description": "cielo despejado", "icon": "01d"}],
    "wind": {"speed": 3.2},
}


def _get_simulado(url: str) -> dict:
    """Simula una llamada HTTP GET devolviendo datos fijos."""
    return RESPUESTA_API_SIMULADA


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Función con type hints que obtiene JSON
# Implementa `fetch_json` que recibe una URL (str) y retorna un dict.
# Debe llamar a `_get_simulado(url)` y retornar el resultado.
# Type hints obligatorios en la firma.
# Pista: sección 5 (Type Hints — TypedDict y Literal) en 01_conceptos.md
def fetch_json(url: str) -> dict:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — Leer variable de entorno con fallback
# Implementa `get_api_key` que:
#   - Lee la variable de entorno cuyo nombre recibe como parámetro (env_var: str)
#   - Si no existe, retorna el valor de `default` (Optional[str], por defecto None)
#   - Type hints completos en la firma
# Pista: sección 6 (Variables de entorno y .env) en 01_conceptos.md
def get_api_key(env_var: str, default: Optional[str] = None) -> Optional[str]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — Parsear respuesta JSON de clima
# Implementa `format_weather` que recibe un dict con la estructura:
#   {
#       "name": str,              # nombre de la ciudad
#       "main": {"temp": float},  # temperatura en Celsius
#       "weather": [{"description": str}]  # descripción del tiempo
#   }
# y retorna un string con el formato:
#   "Valencia: 22.5°C — cielo despejado"
# Pista: sección 4 (httpx — cliente HTTP con control de errores) en 01_conceptos.md
def format_weather(data: dict) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo — muestra los resultados (no modificar)
# ---------------------------------------------------------------------------

def demo() -> None:
    print("=== Ejercicio 1: fetch_json ===")
    resultado = fetch_json("https://api.openweathermap.org/data/2.5/weather?q=Valencia")
    if resultado is not None:
        print(f"Ciudad recibida: {resultado.get('name')}")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 2: get_api_key ===")
    os.environ["MI_API_KEY"] = "clave-de-prueba-123"
    clave = get_api_key("MI_API_KEY", default="sin-clave")
    clave_ausente = get_api_key("CLAVE_INEXISTENTE", default="sin-clave")
    if clave is not None:
        print(f"Clave encontrada: {clave}")
        print(f"Clave ausente con default: {clave_ausente}")
    else:
        print("Sin implementar aún.")

    print("\n=== Ejercicio 3: format_weather ===")
    mensaje = format_weather(RESPUESTA_API_SIMULADA)
    if mensaje is not None:
        print(mensaje)
    else:
        print("Sin implementar aún.")


if __name__ == "__main__":
    demo()
