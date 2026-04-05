"""match/case sobre estructuras: mapping patterns y secuencias anidadas.

Demuestra patrones sobre dicts reales (formato webhook de GitHub-like):
- Mapping pattern con captura: {"autor": user} extrae el valor de "autor" en user
- Secuencia dentro de mapping: {"archivos": [primer_archivo, *_]} captura
  el primer elemento de la lista e ignora el resto con *_
- Patrón parcial: solo se verifican las claves declaradas; claves extra se ignoran
- Wildcard de dict: {"evento": evento_desconocido} captura cualquier valor de "evento"

Los tres payloads del script ejercitan tres ramas distintas del match.

Ejecutar (desde curso/):
    uv run python scripts/clase_02/conceptos/02_match_case_estructuras.py
"""


def parsear_webhook(payload: dict) -> str:
    match payload:
        case {"evento": "commit", "autor": user, "archivos": [primer_archivo, *_]}:
            return f"El usuario {user} subió código tocando {primer_archivo} y más."
        case {"evento": "issue", "accion": "abierto", "id": issue_id}:
            return f"Nuevo ticket abierto con ID: {issue_id}"
        case {"evento": evento_desconocido}:
            return f"Evento sin soporte: {evento_desconocido}"
        case _:
            return "Payload inválido. Faltan claves estructurales."


payloads = [
    {"evento": "commit", "autor": "DevOps", "archivos": [
        "main.py", "test.py"], "hash": "a1b2"},
    {"evento": "issue", "accion": "abierto", "id": 994},
    {"evento": "ping", "timestamp": 123456}
]

for p in payloads:
    print(parsear_webhook(p))
