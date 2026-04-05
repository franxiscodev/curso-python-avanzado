"""
Src Layout — Aislamiento del paquete durante el desarrollo
===========================================================
Muestra si el directorio actual está expuesto en sys.path,
lo que indica si el paquete puede importarse directamente del disco
(flat-layout, riesgo de import shadowing) o solo a través del
entorno instalado (src-layout, comportamiento seguro).

Conceptos que ilustra:
- Flat-layout: el directorio raíz está en sys.path → import sin instalar posible.
- Src-layout: solo src/ está en sys.path vía el .pth del entorno instalado.

Ejecutar:
    uv run python scripts/clase_01/conceptos/02_src_layout_demo.py
"""

import sys
from pathlib import Path


def inspect_path():
    current_dir = str(Path.cwd())
    is_in_path = current_dir in sys.path

    print(f"¿Directorio actual expuesto en sys.path?: {is_in_path}")
    print("En un flat-layout esto sería True. Con src-layout, es mitigado.")


if __name__ == "__main__":
    inspect_path()
