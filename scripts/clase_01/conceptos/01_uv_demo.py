"""Demo UV — Clase 1, Concepto 1.

Muestra que UV instaló las dependencias correctamente.

Comandos que UV ejecuta por ti (no se pueden correr desde Python):
    uv init pycommute        # crea proyecto con pyproject.toml
    uv add httpx             # añade dependencia + actualiza uv.lock
    uv run python script.py  # ejecuta en el entorno gestionado por UV

Ejecuta este script con:
    uv run scripts/clase_01/conceptos/01_uv_demo.py
"""

import httpx

print(f"httpx version: {httpx.__version__}")
print("Si ves esto, UV instaló httpx correctamente.")
