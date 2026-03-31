"""
Ejercicios — Clase 12: API REST con FastAPI
===========================================
Cuatro ejercicios sobre rutas, parámetros, dependencias y tests con TestClient.

Ejecutar (desde curso/):
    uv run python scripts/clase_12/ejercicios_clase_12.py

Requisito: usa fastapi y httpx — disponibles en el entorno del curso.
"""

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

# La aplicación se construye progresivamente en este archivo
app = FastAPI(title="PyCommute API — Ejercicios Clase 12")


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Ruta GET /health
# Añade a `app` una ruta GET en "/health" que retorne:
#   {"status": "ok", "version": "1.0"}
# No recibe parámetros.
# Pista: repasa "Rutas básicas con FastAPI" en 01_conceptos.md
#
# @app.get("/health")
# def health_check() -> dict:
#     pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — Ruta GET /weather/{city} con query param
# Añade a `app` una ruta GET en "/weather/{city}" que:
#   - Reciba `city` como path parameter (str)
#   - Reciba `units` como query parameter con valor por defecto "celsius"
#   - Retorne un dict simulando datos de clima:
#     {"city": city, "temperature": 22.5, "units": units, "description": "soleado"}
# Pista: repasa "Path y query parameters" en 01_conceptos.md
#
# @app.get("/weather/{city}")
# def get_weather(city: str, units: str = "celsius") -> dict:
#     pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — Dependencia verify_token con Depends()
# Implementa la función `verify_token(x_api_token: str = Header(...)) -> str`
# Que:
#   - Lee el header "X-Api-Token"
#   - Si el token es "secreto-123", lo retorna
#   - Si no, lanza HTTPException con status_code=401 y detail="Token inválido"
# Luego añade una ruta GET "/protected" que use Depends(verify_token) y retorne:
#   {"message": "Acceso autorizado", "token": <el token>}
# Pista: repasa "Depends() e inyección de dependencias" en 01_conceptos.md
#
# def verify_token(x_api_token: str = Header(...)) -> str:
#     pass  # ← reemplazar con tu implementación
#
# @app.get("/protected")
# def protected_route(token: str = Depends(verify_token)) -> dict:
#     pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 4
# ---------------------------------------------------------------------------

# TODO: Ejercicio 4 — Tests con TestClient
# Completa la función `run_tests()` que usa TestClient(app) para verificar:
#   a) GET /health retorna status 200 y body tiene key "status"
#   b) GET /weather/Madrid retorna status 200 y body["city"] == "Madrid"
#   c) GET /protected sin token retorna status 422 (header requerido faltante)
#   d) GET /protected con header X-Api-Token: secreto-123 retorna status 200
# Imprime PASS o FAIL para cada verificación.
# Pista: repasa "TestClient y pruebas de integración" en 01_conceptos.md
def run_tests() -> None:
    client = TestClient(app)
    print("=== Ejercicio 4: Tests con TestClient ===")
    # TODO: implementar las 4 verificaciones
    print("  Sin implementar aún.")


# ---------------------------------------------------------------------------
# Demo — ejecuta las verificaciones (no modificar el bloque principal)
# ---------------------------------------------------------------------------

def demo() -> None:
    client = TestClient(app)

    print("=== Ejercicio 1: GET /health ===")
    try:
        resp = client.get("/health")
        if resp.status_code == 200:
            print(f"  Status: {resp.status_code} — Body: {resp.json()}")
        else:
            print(f"  Ruta no implementada (status {resp.status_code})")
    except Exception as e:
        print(f"  Sin implementar aún: {e}")

    print("\n=== Ejercicio 2: GET /weather/Valencia?units=fahrenheit ===")
    try:
        resp = client.get("/weather/Valencia", params={"units": "fahrenheit"})
        if resp.status_code == 200:
            print(f"  Body: {resp.json()}")
        else:
            print(f"  Ruta no implementada (status {resp.status_code})")
    except Exception as e:
        print(f"  Sin implementar aún: {e}")

    print("\n=== Ejercicio 3: GET /protected ===")
    try:
        resp_sin_token = client.get("/protected")
        print(f"  Sin token → status {resp_sin_token.status_code}")
        resp_token_malo = client.get("/protected", headers={"X-Api-Token": "malo"})
        print(f"  Token malo → status {resp_token_malo.status_code}")
        resp_token_ok = client.get("/protected", headers={"X-Api-Token": "secreto-123"})
        print(f"  Token ok → status {resp_token_ok.status_code} — {resp_token_ok.json()}")
    except Exception as e:
        print(f"  Sin implementar aún: {e}")

    print()
    run_tests()


if __name__ == "__main__":
    demo()
