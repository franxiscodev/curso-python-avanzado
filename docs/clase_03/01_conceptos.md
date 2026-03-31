# Clase 3 — Resiliencia Profesional: Loguru, Pydantic-Settings y Tenacity

## 1. Loguru — logging estructurado

El módulo estándar `logging` de Python cumple su función, pero su configuración es verbosa y propensa a errores. **Loguru** ofrece una API mínima con salida estructurada lista desde el primer uso.

### Instalación

```bash
# Windows (PowerShell) y Linux (idéntico)
uv add loguru
```

### Uso básico

```python
from loguru import logger

logger.info("Servicio iniciado")
logger.warning("Cuota al 80%")
logger.error("No se pudo conectar al servidor")
```

### Niveles disponibles (de menor a mayor severidad)

| Nivel       | Uso típico                                              |
|-------------|----------------------------------------------------------|
| `TRACE`     | Diagnóstico muy granular, solo en desarrollo local      |
| `DEBUG`     | Valores intermedios útiles para depurar                 |
| `INFO`      | Eventos normales del flujo principal                    |
| `SUCCESS`   | Operación completada con éxito (exclusivo de Loguru)    |
| `WARNING`   | Situación inesperada pero recuperable                   |
| `ERROR`     | Fallo en una operación específica                       |
| `CRITICAL`  | Fallo que impide continuar la ejecución                 |

### Por qué `logger.info("msg {key}", key=val)` en lugar de f-strings

Loguru soporta *lazy interpolation*: los valores no se evalúan si el nivel está filtrado. Con f-strings el valor siempre se calcula, aunque el mensaje nunca se escriba.

```python
# Malo — el objeto se serializa aunque el nivel esté desactivado
logger.debug(f"Respuesta completa: {response.json()}")

# Correcto — la serialización solo ocurre si DEBUG está activo
logger.debug("Respuesta completa: {payload}", payload=response.json())
```

Además, la interpolación con claves nombradas facilita la búsqueda posterior en logs estructurados (JSON, Elastic, etc.).

### Ejemplo completo

```python
from loguru import logger

def fetch_sensor_data(sensor_id: str) -> dict:
    logger.info("Consultando sensor {sensor_id}", sensor_id=sensor_id)
    # ... lógica de consulta ...
    data = {"temperature": 22.5, "humidity": 60}
    logger.success("Datos obtenidos para sensor {sensor_id}", sensor_id=sensor_id)
    return data
```

▶ **Ejecuta el ejemplo completo:**
```bash
# Windows (PowerShell) y Linux (idéntico)
uv run scripts/clase_03/conceptos/01_loguru_basico.py
```

---

## 2. Loguru vs print vs logging estándar

### Tabla comparativa

| Característica             | `print()`       | `logging` estándar          | `loguru`                        |
|----------------------------|-----------------|-----------------------------|---------------------------------|
| Configuración inicial      | Ninguna         | Verbosa (handlers, formatters) | Cero — funciona al importar  |
| Niveles                    | No              | Sí                          | Sí (+ `SUCCESS` y `TRACE`)     |
| Timestamps                 | Manual          | Configurable                | Automáticos                     |
| Nombre del módulo origen   | Manual          | Configurable                | Automático                      |
| Colores en terminal        | Manual (ANSI)   | No por defecto              | Automáticos                     |
| Rotación de archivos       | No              | `RotatingFileHandler`       | `logger.add("app.log", rotation="10 MB")` |
| Lazy interpolation         | No              | Sí (`%s` style)             | Sí (`{key}` style)              |
| Excepciones con traceback  | Manual          | `logger.exception()`        | `logger.exception()` mejorado  |
| Integración con `sink`     | No              | Handlers                    | Cualquier callable o archivo   |

### Cuándo Loguru gana

- Proyectos nuevos donde no existe infraestructura de logging previa
- Scripts y servicios donde la configuración rápida es prioritaria
- Equipos pequeños que prefieren convención sobre configuración

### Cuándo el `logging` estándar es necesario

- Librerías publicadas en PyPI — las librerías **nunca** deben imponer Loguru a quien las consume; el `logging` estándar permite que el usuario final configure el output
- Sistemas legados con handlers ya configurados que no se pueden migrar
- Entornos donde la política de la organización exige el módulo estándar

```python
# Patrón correcto en una librería reutilizable
import logging

logger = logging.getLogger(__name__)  # el usuario decide cómo manejarlo

def process(data: list) -> list:
    logger.debug("Procesando %d elementos", len(data))
    return data
```

▶ **Ejecuta el ejemplo completo:**
```bash
# Windows (PowerShell) y Linux (idéntico)
uv run scripts/clase_03/conceptos/02_loguru_formato.py
```

---

## 3. Pydantic-Settings — configuración validada

`pydantic-settings` extiende Pydantic para leer variables de entorno (y archivos `.env`) y validarlas como campos tipados. El resultado es un objeto de configuración que garantiza tipos correctos desde el arranque.

### Instalación

```bash
# Windows (PowerShell) y Linux (idéntico)
uv add pydantic-settings
```

### Estructura básica

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "MyApp"
    debug: bool = False
    api_key: str                 # sin default → campo requerido
```

### Cómo lee los valores

1. Variables de entorno del sistema operativo (mayor precedencia)
2. Archivo `.env` indicado en `SettingsConfigDict`
3. Valores por defecto definidos en la clase

```python
# .env
APP_NAME=ProductionService
DEBUG=false
API_KEY=sk-abc123
```

```python
settings = AppSettings()
print(settings.app_name)   # "ProductionService"
print(settings.debug)      # False  ← str "false" convertido a bool automáticamente
print(settings.api_key)    # "sk-abc123"
```

### Campos opcionales con defaults

```python
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "DefaultApp"
    debug: bool = False
    max_retries: int = 3
    api_key: str                 # requerido — sin default
    base_url: str = "https://api.example.com"
```

### Patrón de uso: instancia única

```python
# config.py
from functools import lru_cache

@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
```

`lru_cache` garantiza que `.env` se lee una sola vez durante toda la ejecución.

▶ **Ejecuta el ejemplo completo:**
```bash
# Windows (PowerShell) y Linux (idéntico)
uv run scripts/clase_03/conceptos/03_pydantic_settings.py
```

---

## 4. El patrón fail-fast

### Por qué fallar al arrancar es mejor que fallar en runtime

Un servicio que arranca sin configuración válida fallará eventualmente — pero en el peor momento: cuando ya está en producción y procesando peticiones reales. El patrón **fail-fast** exige que cualquier error de configuración se detecte en el momento del inicio, no durante la ejecución.

```
Fail-fast:   arranque → ValidationError → proceso termina → el operador lo corrige
Sin fail-fast: arranque → OK → 3 horas después → None silencioso → datos corruptos
```

### `os.getenv()` vs Pydantic-Settings

```python
# Sin fail-fast — os.getenv()
import os

api_key = os.getenv("API_KEY")           # devuelve None sin avisar
response = client.get(url, headers={"Authorization": f"Bearer {api_key}"})
# Bearer None — la API falla con 401; el error parece un problema de red
```

```python
# Con fail-fast — Pydantic-Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str                          # campo requerido

settings = Settings()                     # ValidationError aquí si falta API_KEY
# Si llega a esta línea, api_key es un str válido — garantizado
response = client.get(url, headers={"Authorization": f"Bearer {settings.api_key}"})
```

### Ventajas concretas

| Aspecto              | `os.getenv()`                    | Pydantic-Settings                        |
|----------------------|----------------------------------|------------------------------------------|
| Key faltante         | `None` sin aviso                 | `ValidationError` inmediato              |
| Tipo incorrecto      | Siempre `str` o `None`           | Conversión automática + error si falla   |
| Documentación        | Dispersa en el código            | Centralizada en la clase `Settings`      |
| Testabilidad         | Mockear `os.environ`             | Pasar valores por constructor o env vars |
| Detección del error  | En runtime, al usar el valor     | En startup, antes de procesar nada       |

### Regla práctica

Si una variable de entorno es necesaria para que el servicio funcione correctamente, debe ser un campo **requerido** (sin default) en `BaseSettings`. Si el servicio puede operar sin ella con un comportamiento diferente, usar un default explícito.

---

## 5. Tenacity — `@retry` básico

Las llamadas a sistemas externos (APIs HTTP, bases de datos, colas de mensajes) fallan ocasionalmente por razones transitorias: timeouts de red, sobrecarga momentánea del servidor, interrupciones de conexión. **Tenacity** implementa el patrón retry con control preciso sobre cuándo y cómo reintentar.

### Instalación

```bash
# Windows (PowerShell) y Linux (idéntico)
uv add tenacity
```

### Decorador básico

```python
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
def fetch_data(url: str) -> dict:
    response = httpx.get(url, timeout=5.0)
    response.raise_for_status()
    return response.json()
```

### Parámetros principales

| Parámetro                   | Propósito                                                   |
|-----------------------------|-------------------------------------------------------------|
| `stop_after_attempt(n)`     | Máximo `n` intentos antes de propagar la excepción          |
| `wait_fixed(seconds)`       | Espera fija entre intentos                                  |
| `retry_if_exception_type()` | Solo reintenta si la excepción es del tipo indicado         |
| `reraise=True`              | Propaga la excepción original al agotar los intentos        |

### Por qué limitar las condiciones de retry a errores transitorios

Esta es la regla más importante al usar Tenacity. Reintentar ante cualquier excepción puede ocultar bugs reales o empeorar el problema.

**Errores transitorios** (sí reintentar):
- `httpx.ConnectError` — la red falló momentáneamente
- `httpx.TimeoutException` — el servidor tardó más de lo esperado
- `ConnectionResetError` — la conexión se interrumpió

**Errores deterministas** (no reintentar — siempre fallarán igual):
- `httpx.HTTPStatusError` con status 400 — datos de entrada incorrectos
- `httpx.HTTPStatusError` con status 401 — API key inválida
- `ValueError` — el JSON recibido no tiene el formato esperado
- Cualquier excepción de lógica propia del programa

```python
# Incorrecto — reintenta ante cualquier error, incluyendo 401 y bugs
@retry(stop=stop_after_attempt(3))
def fetch_sensor(sensor_id: str) -> dict: ...

# Correcto — solo reintenta ante fallos de red y timeouts
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
def fetch_sensor(sensor_id: str) -> dict: ...
```

### `wait_exponential` — variante para producción

En producción se prefiere espera exponencial para no saturar un servidor que ya está bajo carga:

```python
from tenacity import wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=30),  # 1s, 2s, 4s, 8s, 16s (cap 30s)
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
def fetch_data_production(url: str) -> dict: ...
```

`wait_fixed` es adecuado para desarrollo y tests; `wait_exponential` es el estándar en servicios productivos.

▶ **Ejecuta el ejemplo completo:**
```bash
# Windows (PowerShell) y Linux (idéntico)
uv run scripts/clase_03/conceptos/04_tenacity_retry.py
```
