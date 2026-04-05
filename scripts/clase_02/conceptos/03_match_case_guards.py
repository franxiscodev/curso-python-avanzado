"""match/case con guards: condiciones sobre valores capturados.

Demuestra el patrón case {"key": var} if condicion:
- El patrón captura el valor en una variable
- El guard evalúa esa variable con una condición adicional
- Solo si ambos se cumplen se ejecuta el bloque

procesar_compra() combina guards con patrones de mapping:
- if total > 1000 — guard sobre variable capturada del dict
- "items": [] — patrón que solo coincide si la lista está vacía (sin guard)
- El tercer case es el fallback para compras normales

El orden de los cases importa: el guard de fraude (> 1000) va primero.

Ejecutar (desde curso/):
    uv run python scripts/clase_02/conceptos/03_match_case_guards.py
"""


def procesar_compra(carro: dict) -> str:
    match carro:
        # Extraemos variables Y aplicamos lógica de negocio de inmediato
        case {"usuario": u, "total": total} if total > 1000:
            return f"Alerta de Fraude: Bloquear compra de {u} por ${total}"

        case {"usuario": u, "items": []}:
            return f"{u} intentó comprar un carrito vacío."

        case {"usuario": u, "total": total}:
            return f"Compra aprobada para {u} por ${total}"

        case _:
            return "Estructura de carrito corrupta."


carritos = [
    {"usuario": "Alice", "total": 1500, "items": ["Laptop"]},
    {"usuario": "Bob", "total": 0, "items": []},
    {"usuario": "Charlie", "total": 45, "items": ["Cable USB"]}
]

for c in carritos:
    print(procesar_compra(c))
