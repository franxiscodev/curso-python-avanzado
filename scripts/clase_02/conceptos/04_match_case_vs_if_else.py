"""Demo match/case vs if/elif/else — Clase 2, Concepto 4.

Comparativa directa del mismo problema con ambos enfoques.
match/case gana legibilidad cuando la estructura del dato importa.
if/elif es preferible cuando la condición es aritmética o booleana simple.

Ejecuta este script con:
    uv run scripts/clase_02/conceptos/04_match_case_vs_if_else.py
"""

data = {"status": "ok", "value": 42}

# --- Con if/elif/else ---
# Hay que verificar la existencia de cada clave manualmente
if "status" in data and data["status"] == "ok" and "value" in data:
    resultado_if = f"Valor: {data['value']}"
elif "status" in data and data["status"] == "error" and "message" in data:
    resultado_if = f"Error: {data['message']}"
else:
    resultado_if = "Desconocido"

# --- Con match/case ---
# El patrón describe la estructura esperada — más declarativo
match data:
    case {"status": "ok", "value": v}:
        resultado_match = f"Valor: {v}"
    case {"status": "error", "message": msg}:
        resultado_match = f"Error: {msg}"
    case _:
        resultado_match = "Desconocido"

print(f"if/else:    {resultado_if}")
print(f"match/case: {resultado_match}")
print()
print("Mismo resultado. match/case es mas legible con estructuras complejas.")
print("Regla: usa match/case cuando parseas JSONs o estructuras de datos.")
