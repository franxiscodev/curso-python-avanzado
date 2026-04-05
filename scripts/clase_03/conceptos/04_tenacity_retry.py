"""Tenacity: @retry con espera exponencial entre intentos.

Demuestra el patrón de reintentos automáticos con backoff exponencial:
- stop_after_attempt(4): máximo 4 intentos totales
- wait_exponential(min=1, max=10): espera 1s → 2s → 4s entre intentos

llamar_api_externa() simula una API caída los primeros 3 intentos
y exitosa en el 4to. La función se llama automáticamente sin código
de bucle manual — tenacity gestiona el flujo completo.

Si todos los intentos fallan, ConnectionError se propaga al llamador.

Ejecutar (desde curso/):
    uv run python scripts/clase_03/conceptos/04_tenacity_retry.py
"""

import time
from tenacity import retry, stop_after_attempt, wait_exponential

intentos_realizados = 0

# stop: máximo 4 intentos (incluye el primero)
# wait: espera exponencial — 1s, 2s, 4s entre intentos (cap 10s)


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def llamar_api_externa():
    global intentos_realizados
    intentos_realizados += 1

    print(f"[Intento {intentos_realizados}] Conectando a la API...")

    # Los primeros 3 intentos simulan que la API está caída
    if intentos_realizados < 4:
        raise ConnectionError("Timeout: El servidor remoto no responde.")

    # El 4to intento tiene éxito — tenacity deja de reintentar y retorna
    return "Datos obtenidos con exito."


print("Iniciando proceso de extracción de datos...")
try:
    resultado = llamar_api_externa()
    print(resultado)
except ConnectionError as e:
    print("La API está caída definitivamente. Deteniendo proceso.")
