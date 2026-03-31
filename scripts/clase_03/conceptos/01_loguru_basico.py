"""Demo Loguru básico — Clase 3, Concepto 1.

Loguru reemplaza print() para output de aplicaciones.
Ventajas sobre print(): nivel, timestamp, módulo y línea incluidos
automáticamente. Sin configuración inicial.

Ejecuta este script con:
    uv run scripts/clase_03/conceptos/01_loguru_basico.py
"""

from loguru import logger

logger.debug("Mensaje de debug — solo en desarrollo")
logger.info("Aplicacion iniciada correctamente")
logger.warning("La respuesta tardo mas de lo esperado")
logger.error("No se pudo conectar al servicio externo")
logger.success("Operacion completada exitosamente")
