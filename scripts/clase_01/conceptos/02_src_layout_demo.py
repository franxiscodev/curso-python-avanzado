"""Demo src layout — Clase 1, Concepto 2.

Muestra por qué el src layout garantiza imports correctos.

Con src layout, Python solo puede importar el paquete si está
correctamente instalado (via `uv sync`). Sin src layout, un
`import pycommute` podría encontrar accidentalmente la carpeta
local sin que el paquete esté instalado.

Ejecuta este script con:
    uv run scripts/clase_01/conceptos/02_src_layout_demo.py
"""

import importlib.util
import sys


def check_package(name: str) -> None:
    spec = importlib.util.find_spec(name)
    if spec is None:
        print(f"{name}: NO encontrado")
    else:
        print(f"{name}: encontrado en {spec.origin}")


print(f"Python ejecutándose desde: {sys.executable}")
print()

check_package("httpx")
check_package("pycommute")
check_package("paquete_inexistente")
