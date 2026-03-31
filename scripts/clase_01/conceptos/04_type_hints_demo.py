"""Demo Type Hints — Clase 1, Concepto 4.

Muestra la diferencia entre funciones con y sin type hints,
y por qué Python NO valida tipos en runtime (eso es trabajo de mypy).

Ejecuta este script con:
    uv run scripts/clase_01/conceptos/04_type_hints_demo.py
"""


# Sin type hints — el IDE no sabe qué esperar ni qué devuelve
def greet_untyped(name):
    return f"Hola {name}"


# Con type hints — el IDE autocompleta y mypy detecta errores
def greet(name: str) -> str:
    return f"Hola {name}"


# Python no valida en runtime — esto no lanza error:
result = greet(42)  # type: ignore
print(result)       # "Hola 42" — Python lo acepta igual

print()
print("Type hints son para el IDE y mypy, no para Python en runtime.")
print("Para validación en runtime se usa Pydantic (Clase 8).")
