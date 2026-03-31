"""Demo match/case básico — Clase 2, Concepto 1.

Patrones literales y wildcard sobre tipos simples.
Equivale a un switch/case de otros lenguajes, pero más potente.

Python 3.10+ requerido. Verificar con:
    python --version

Ejecuta este script con:
    uv run scripts/clase_02/conceptos/01_match_case_basico.py
"""


def clasificar_codigo(codigo: int) -> str:
    match codigo:
        case 200:
            return "OK"
        case 404:
            return "No encontrado"
        case 500:
            return "Error del servidor"
        case _:
            return f"Codigo desconocido: {codigo}"


for c in [200, 404, 500, 418]:
    print(f"{c} -> {clasificar_codigo(c)}")
