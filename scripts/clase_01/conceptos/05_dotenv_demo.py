"""
Variables de entorno y .env — Gestión segura de secretos
==========================================================
Demuestra el ciclo completo: crear un .env temporal, inyectarlo en
os.environ con python-dotenv, consumir los valores y limpiar el archivo.

Conceptos que ilustra:
- load_dotenv(override=True): inyecta el .env en os.environ sin modificar el código.
- os.getenv con default: acceso seguro que no lanza KeyError si la variable falta.
- Enmascaramiento: nunca loguear secrets completos; mostrar solo los extremos.
- finally: el archivo se borra aunque el código anterior falle (limpieza garantizada).

Ejecutar:
    uv run python scripts/clase_01/conceptos/05_dotenv_demo.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def test_real_env_injection():
    # 1. Definimos la ruta de nuestro archivo secreto temporal
    env_path = Path(".env.local")

    try:
        # 2. Escribimos el archivo físicamente en el disco
        print(f"[*] Creando archivo {env_path.name} en disco...")
        env_path.write_text("API_KEY=sk-live-123456789\nAPP_ENV=produccion\n")
        # ← Muestra ruta completa
        print(f"[*] El archivo se creará en: {env_path.absolute()}")

        # 3. La Magia: python-dotenv lee el archivo y lo inyecta en os.environ
        # override=True fuerza a sobreescribir si la variable ya existía en tu terminal
        load_dotenv(dotenv_path=env_path, override=True)
        print("[*] Secretos inyectados en memoria.\n")

        # 4. Consumo seguro
        api_key = os.getenv("API_KEY")
        entorno = os.getenv("APP_ENV", "desarrollo")

        # Enmascaramos la clave para los logs (regla de oro en producción)
        masked_key = f"{api_key[:7]}...{api_key[-4:]}" if api_key else "NO_ENCONTRADA"

        print(f"[ENV] Entorno activo: {entorno}")
        print(f"[KEY] API Key cargada: {masked_key}")

    finally:
        # 5. Destrucción de la evidencia (Limpieza)
        # El bloque finally garantiza que el archivo se borre incluso si el código anterior falla
        if env_path.exists():
            env_path.unlink()
            print(f"\n[*] Limpieza: {env_path.name} eliminado del disco.")


if __name__ == "__main__":
    test_real_env_injection()
