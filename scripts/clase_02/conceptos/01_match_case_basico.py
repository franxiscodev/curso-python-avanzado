"""match/case básico: literales, OR y wildcard sobre strings.

Demuestra los tres bloques fundamentales de match/case:
- Literal: case "EXITO" — coincide con un valor exacto
- OR pattern: case "PENDIENTE" | "PROCESANDO" — agrupa dos literales en un case
- Wildcard: case _ — captura cualquier valor que no coincidió antes

procesar_estado_pago() normaliza la entrada con .upper() antes del match,
lo que hace que "exito", "EXITO" y "Exito" sean equivalentes.

Ejecutar (desde curso/):
    uv run python scripts/clase_02/conceptos/01_match_case_basico.py
"""


def procesar_estado_pago(estado: str) -> str:
    match estado.upper():
        case "EXITO":
            return "El pago se ha completado."
        case "PENDIENTE" | "PROCESANDO":
            return "El pago está en la cola de validación."
        case "FALLIDO":
            return "Transacción rechazada."
        case _:
            return f"Estado anómalo detectado: {estado}"


estados = ["exito", "Procesando", "REEMBOLSADO"]
for e in estados:
    print(f"{e:12} -> {procesar_estado_pago(e)}")
