"""Demo python-dotenv — Clase 1, Concepto 5.

Muestra el patrón .env / .env.example:
- .env.example: plantilla versionada en git (valores falsos)
- .env: valores reales, NUNCA en git (.gitignore)

Crea un .env temporal para la demo y lo elimina al final.

Ejecuta este script con:
    uv run scripts/clase_01/conceptos/05_dotenv_demo.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Crear .env temporal para la demo
env_file = Path(".env.demo")
env_file.write_text("DEMO_KEY=hola_desde_dotenv\nAPP_ENV=demo\n")

load_dotenv(env_file)

print(f"DEMO_KEY: {os.getenv('DEMO_KEY')}")
print(f"APP_ENV:  {os.getenv('APP_ENV')}")
print(f"KEY_INEXISTENTE: {os.getenv('KEY_INEXISTENTE', 'valor_por_defecto')}")

# Limpiar
env_file.unlink()
print("\n.env temporal eliminado.")
