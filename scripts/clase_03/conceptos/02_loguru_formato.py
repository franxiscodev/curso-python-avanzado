"""Loguru avanzado: evaluación perezosa y contexto con bind().

Demuestra dos técnicas que van más allá del uso básico:

1. EVALUACIÓN PEREZOSA (lazy):
   generar_reporte_pesado() simula una operación costosa de CPU.
   Con f-string, la función se ejecuta aunque el nivel filtre el mensaje.
   Con lambda en logger.debug("...", lambda: fn()), la función NO se ejecuta.
   El sink está en WARNING — el DEBUG se filtra, y la función nunca corre.

2. CONTEXTO INYECTADO (bind):
   logger.bind(user_id=..., ip=...) retorna un sub-logger con esos campos pegados.
   Cada llamada a user_logger lleva los campos automáticamente — sin repetirlos.

Ejecutar (desde curso/):
    uv run python scripts/clase_03/conceptos/02_loguru_formato.py
"""

from loguru import logger


def generar_reporte_pesado():
    print("--- ⚠️ ATENCIÓN: Consumiendo CPU pesadamente ---")
    return "Reporte PDF Generado"


# 1. EVALUACIÓN PEREZOSA (LAZY)
# Cambia esto a "INFO" y verás que la función pesada NUNCA se ejecuta.
logger.remove()
logger.add(lambda msg: print(msg, end=""), level="WARNING")

# Incorrecto: La función se ejecuta aunque el log esté en WARNING
# logger.debug(f"Datos: {generar_reporte_pesado()}")

# Correcto: La función no se ejecuta porque usamos lambdas
logger.debug("Datos: {}", lambda: generar_reporte_pesado())

# 2. CONTEXTO INYECTADO (BIND)
# Creamos un sub-logger para rastrear a un usuario específico
user_logger = logger.bind(user_id="usr_99X", ip="192.168.1.5")
user_logger.warning("Intento de login fallido.")
user_logger.warning("Contraseña restablecida.")
