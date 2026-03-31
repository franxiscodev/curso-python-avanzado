"""Demo Loguru formato estructurado — Clase 3, Concepto 2.

Por qué NO usar f-strings con logger:
1. Las f-strings se evalúan siempre, aunque el nivel esté desactivado.
2. Los parámetros nombrados son buscables en herramientas de log (Kibana, etc.).
3. Loguru puede serializar a JSON manteniendo los valores como campos separados.

Ejecuta este script con:
    uv run scripts/clase_03/conceptos/02_loguru_formato.py
"""

from loguru import logger

ciudad = "Valencia"
temperatura = 13.5
intentos = 3

# Correcto: lazy evaluation, campos buscables
logger.info("Clima consultado para {ciudad}: {temperatura}C", ciudad=ciudad, temperatura=temperatura)
logger.warning("Reintentando (intento {n} de 3)", n=intentos)

# Incorrecto: la f-string se evalua aunque DEBUG este desactivado
# logger.debug(f"Respuesta: {temperatura}")  # evitar

# Con contexto adicional usando bind()
request_logger = logger.bind(request_id="abc-123", user="demo")
request_logger.info("Peticion procesada")
request_logger.error("Peticion fallida")
