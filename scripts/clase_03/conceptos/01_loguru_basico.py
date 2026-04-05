"""Loguru: dos sinks con niveles distintos — consola e archivo.

Demuestra la configuración básica de loguru con múltiples destinos:
- logger.remove() elimina el sink por defecto (stderr sin filtro)
- stderr recibe solo INFO en adelante — lo que el operador debe ver
- "sistema_auditoria.log" recibe DEBUG en adelante — el historial completo

Resultado al ejecutar:
  - En consola: solo INFO y ERROR (DEBUG queda fuera del nivel de consola)
  - En archivo: los tres niveles, incluido DEBUG

Ejecutar (desde curso/):
    uv run python scripts/clase_03/conceptos/01_loguru_basico.py
"""

import sys
from loguru import logger

# Eliminamos el sink por defecto para controlar exactamente qué va a dónde
logger.remove()
logger.add(sys.stderr, level="INFO", colorize=True)         # operadores: INFO+
logger.add("sistema_auditoria.log", level="DEBUG", rotation="1 MB")  # auditoría: todo


def procesar_datos():
    # DEBUG: detalle técnico — solo va al archivo, nunca a la consola del operador
    logger.debug("Iniciando bucle de procesamiento de 10k registros...")
    # INFO: evento normal del flujo — aparece en consola y en archivo
    logger.info("Conexión a la base de datos establecida.")
    # ERROR: fallo en una operación — aparece en consola y en archivo
    logger.error("Timeout al intentar leer la tabla 'usuarios'.")


if __name__ == "__main__":
    procesar_datos()
