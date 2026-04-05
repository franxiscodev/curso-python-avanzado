"""match/case vs if/elif: comparativa sobre el mismo JSON anidado.

Demuestra las dos aproximaciones al mismo problema de parsing:
- parse_imperativo(): if/elif encadenados con accesos .get() y isinstance()
- parse_declarativo(): match/case con patrón de mapping anidado

El dict tiene tres niveles de profundidad:
  datos["tipo"] == "mensaje_texto"
  datos["contenido"]               ← capturado como `msg`
  datos["metadata"]["urgencia"]    ← anidado en el patrón directamente

La versión declarativa expresa la forma esperada del dato en una sola línea
de patrón; la imperativa necesita tres niveles de if anidados para lo mismo.

Ejecutar (desde curso/):
    uv run python scripts/clase_02/conceptos/04_match_case_vs_if_else.py
"""

mensaje = {"tipo": "mensaje_texto", "contenido": "Hola equipo",
           "metadata": {"urgencia": "alta"}}

# --- El infierno del Junior (Imperativo) ---


def parse_imperativo(data: dict) -> str:
    if "tipo" in data and data["tipo"] == "mensaje_texto":
        if "contenido" in data:
            contenido = data["contenido"]
            if "metadata" in data and "urgencia" in data["metadata"] and data["metadata"]["urgencia"] == "alta":
                return f"[URGENTE] Dice: {contenido}"
            return f"Dice: {contenido}"
    return "Desconocido"

# --- El estándar Senior (Declarativo) ---


def parse_declarativo(data: dict) -> str:
    match data:
        case {"tipo": "mensaje_texto", "contenido": msg, "metadata": {"urgencia": "alta"}}:
            return f"[URGENTE] Dice: {msg}"
        case {"tipo": "mensaje_texto", "contenido": msg}:
            return f"Dice: {msg}"
        case _:
            return "Desconocido"


print(f"Resultado Imperativo:  {parse_imperativo(mensaje)}")
print(f"Resultado Declarativo: {parse_declarativo(mensaje)}")
