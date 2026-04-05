"""
UV — Entorno aislado y reproducible
=====================================
Demuestra cómo verificar que el intérprete activo pertenece a un
entorno virtual creado por uv y no al Python del sistema.

Conceptos que ilustra:
- sys.prefix vs sys.base_prefix: el primero apunta al entorno activo;
  el segundo, al Python base del sistema. Si difieren, hay aislamiento.

Ejecutar:
    uv run python scripts/clase_01/conceptos/01_uv_demo.py
"""

import sys


def verify_isolation():
    is_isolated = sys.prefix != sys.base_prefix
    print(f"¿Entorno aislado?: {is_isolated}")
    print(f"Ruta activa: {sys.prefix}")


if __name__ == "__main__":
    verify_isolation()
