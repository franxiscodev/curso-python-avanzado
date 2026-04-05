"""
Type Hints — TypedDict y Literal
==================================
Demuestra cómo TypedDict define la forma exacta de un diccionario
y Literal restringe los valores admitidos a un conjunto fijo.

Conceptos que ilustra:
- TypedDict: contrato de claves y tipos para un dict; el IDE autocompletea las llaves.
- Literal: estrecha el tipo str a valores concretos; mypy rechaza valores fuera del conjunto.
- Las anotaciones no validan en runtime — eso es trabajo de Pydantic (Clase 8).

Ejecutar:
    uv run python scripts/clase_01/conceptos/04_type_hints_demo.py
"""

from typing import TypedDict, Literal

# 1. Definimos la "forma" exacta del diccionario que esperamos procesar


class CommuteRoute(TypedDict):
    origin: str
    destination: str
    distance_km: float
    # Literal fuerza a que el valor deba ser EXACTAMENTE uno de estos strings
    transport_mode: Literal["driving", "walking", "transit"]


def analyze_route(route: CommuteRoute) -> str:
    # 2. El IDE ahora autocompleta las llaves.
    # Si escribimos route["distancia"], Mypy lanzará un error crítico.
    mode = route["transport_mode"]

    # 3. El IDE sabe que 'mode' no es un string cualquiera, es uno de los 3 literales.
    if mode == "walking" and route["distance_km"] > 5.0:
        return f"Caminar de {route['origin']} a {route['destination']} tomará demasiado."

    return f"Ruta viable usando {mode}."


if __name__ == "__main__":
    # 4. Diccionario válido que cumple el contrato
    valid_route: CommuteRoute = {
        "origin": "Casa",
        "destination": "Oficina",
        "distance_km": 2.5,
        "transport_mode": "walking"
    }

    print(analyze_route(valid_route))

    # --- DESCOMENTA ESTO PARA VER CÓMO MYPY EXPLOTA ---
    # invalid_route: CommuteRoute = {
    #     "origin": "Centro",
    #     "distance_km": 10,
    #     "transport_mode": "flying" # 'flying' no está en el Literal. Falta 'destination'.
    # }
    # print(analyze_route(invalid_route))
