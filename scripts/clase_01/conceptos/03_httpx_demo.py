"""
httpx — Resiliencia en llamadas HTTP
=====================================
Demuestra los tres escenarios fundamentales de una llamada HTTP:
exito (200), error del servidor (404) y timeout.

Conceptos que ilustra:
- raise_for_status(): convierte códigos 4xx/5xx en excepciones explícitas.
- HTTPStatusError vs TimeoutException: cada tipo de fallo tiene su propia excepción.
- timeout=3.0: límite innegociable para no bloquear el hilo indefinidamente.

Ejecutar:
    uv run python scripts/clase_01/conceptos/03_httpx_demo.py

Nota: el escenario de timeout tarda ~3 segundos (el cliente aborta la conexión).
"""

import httpx


def test_network_resilience():
    # Establecemos un límite innegociable: 3 segundos máximo por petición
    with httpx.Client(timeout=3.0) as client:

        print("[*] ESCENARIO 1: El Camino Feliz (200 OK)")
        try:
            # Petición exitosa a un endpoint válido
            res_ok = client.get("https://httpbin.org/status/200")
            res_ok.raise_for_status()
            print(
                f"    [OK] Exito absoluto. Codigo de estado: {res_ok.status_code}")
        except httpx.HTTPError as exc:
            print(f"    [ERROR] Esto no deberia ejecutarse: {exc}")

        print("\n[*] ESCENARIO 2: Fallo del Servidor (404 Not Found)")
        try:
            # Pedimos algo que no existe
            res_err = client.get("https://httpbin.org/status/404")
            res_err.raise_for_status()  # Detona la excepción adrede
        except httpx.HTTPStatusError as exc:
            print(
                f"    [CONTROLADO] El servidor rechazo la peticion con codigo {exc.response.status_code}")

        print("\n[*] ESCENARIO 3: La API se queda colgada (Timeout)")
        try:
            # httpbin.org/delay/5 obligará al servidor a tardar 5 segundos en responder.
            # Nuestro cliente tiene un timeout de 3.0 segundos. Va a abortar la misión.
            client.get("https://httpbin.org/delay/5")
        except httpx.TimeoutException:
            print(
                "    [TIMEOUT] La API tardo demasiado. El cliente corto la conexion para salvar el hilo.")
        except httpx.RequestError as exc:
            print(f"    [AVISO] Otro error de red de bajo nivel: {exc}")


if __name__ == "__main__":
    test_network_resilience()
