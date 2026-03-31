"""Demo httpx — Clase 1, Concepto 3.

Muestra una petición GET real con httpx:
- context manager para gestión automática de la conexión
- raise_for_status() para propagar errores HTTP como excepciones

Ejecuta este script con:
    uv run scripts/clase_01/conceptos/03_httpx_demo.py
"""

import httpx


def fetch_sample() -> dict:
    with httpx.Client() as client:
        response = client.get("https://httpbin.org/json")
        response.raise_for_status()
        return response.json()


data = fetch_sample()
print(f"Respuesta recibida: {data}")
