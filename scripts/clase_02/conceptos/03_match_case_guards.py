"""Demo match/case con guards — Clase 2, Concepto 3.

Un guard es una condición adicional después del patrón: `case x if condicion`.
Se evalúa solo si el patrón encaja. Permite refinar casos sin anidar if/else.

Ejecuta este script con:
    uv run scripts/clase_02/conceptos/03_match_case_guards.py
"""


def clasificar_temperatura(data: dict) -> str:
    match data:
        case {"temp": t} if t < 0:
            return "Bajo cero"
        case {"temp": t} if t < 15:
            return "Frio"
        case {"temp": t} if t < 25:
            return "Templado"
        case {"temp": t}:
            return "Calido"
        case _:
            return "Sin datos de temperatura"


mediciones = [{"temp": -5}, {"temp": 10}, {"temp": 22}, {"temp": 35}, {}]
for m in mediciones:
    print(f"{m} -> {clasificar_temperatura(m)}")
