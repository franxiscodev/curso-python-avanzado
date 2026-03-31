"""Demo match/case sobre dicts y listas — Clase 2, Concepto 2.

El caso más útil para parsear respuestas de APIs:
extrae valores de estructuras anidadas en un solo paso.

Ejecuta este script con:
    uv run scripts/clase_02/conceptos/02_match_case_estructuras.py
"""


def procesar_respuesta(data: dict) -> str:
    match data:
        # Patrón de mapping: extrae "value" solo si "status" es "ok"
        case {"status": "ok", "value": v}:
            return f"Valor recibido: {v}"
        # Patrón de mapping: extrae "message" cuando hay error
        case {"status": "error", "message": msg}:
            return f"Error: {msg}"
        # Patrón de secuencia: extrae primer elemento y cuenta el resto
        case {"items": [first, *rest]}:
            return f"Lista: primero={first}, resto={len(rest)} items"
        case _:
            return f"Estructura desconocida: {data}"


casos = [
    {"status": "ok", "value": 42},
    {"status": "error", "message": "timeout"},
    {"items": [1, 2, 3, 4]},
    {"otra": "cosa"},
]
for caso in casos:
    print(procesar_respuesta(caso))
