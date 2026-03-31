# Lab Guide — Clase 3: Resiliencia Profesional

## ¿Por qué construimos esto así?

Reemplazamos dotenv completamente con Pydantic-Settings en lugar de
usarlos juntos. La razón: el alumno ya vivió el problema de os.getenv()
devolviendo None sin aviso. Pydantic-Settings resuelve exactamente ese
problema — y verlo como reemplazo completo hace el contraste obvio.

Aplicamos Loguru y @retry solo a weather.py esta clase, aunque route.py
también los necesita. Un módulo bien hecho es mejor punto de partida
que dos módulos a medias. Route.py recibe el mismo tratamiento en Clase 4.

---

## Dependencias de esta clase

```bash
# Windows (PowerShell) y Linux (idéntico)
uv add loguru pydantic-settings tenacity
```

---

## Pasos del lab

### Paso 1 — Instalar las dependencias

```bash
# Windows (PowerShell) y Linux (idéntico)
uv add loguru pydantic-settings tenacity
```

Concepto aplicado: sección 1 (Loguru), sección 3 (Pydantic-Settings) y sección 5 (Tenacity) de `01_conceptos.md`.

Verifica que `pyproject.toml` ahora incluye las tres librerías bajo el comentario `# Clase 3`.

---

### Paso 2 — Crear `config.py` con Settings

Crea `curso/src/pycommute/config.py` con la clase `Settings`:

- Campos **requeridos** (sin default): `openweather_api_key`, `openrouteservice_api_key`
- Campos **opcionales** con defaults: los que el proyecto pueda necesitar (base URLs, timeouts, nombre de app, etc.)
- `SettingsConfigDict` apuntando a `.env`
- Función `get_settings()` con `@lru_cache(maxsize=1)`

Concepto aplicado: sección 3 de `01_conceptos.md`.

---

### Paso 3 — Verificar el comportamiento fail-fast

1. Abre `.env` y comenta o elimina temporalmente una de las API keys requeridas.
2. Ejecuta el script de demo:

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run python scripts/clase_03/demo_proyecto.py
```

3. Observa el `ValidationError` de Pydantic en la salida — el proceso termina inmediatamente antes de hacer ninguna llamada.
4. Restaura la key en `.env` antes de continuar.

Concepto aplicado: sección 4 de `01_conceptos.md`.

---

### Paso 4 — Actualizar `weather.py`

Añade las siguientes mejoras a `curso/src/pycommute/weather.py`:

**Logging con Loguru:**

```python
from loguru import logger

# Al inicio de la función de consulta:
logger.info("Consultando clima para {city}", city=city)

# Al obtener la respuesta:
logger.success("Clima obtenido: {temp}°C, {description}", temp=temp, description=description)

# En el bloque de error:
logger.error("Error al consultar clima: {error}", error=e)
```

**Retry con Tenacity:**

```python
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
def get_weather(city: str, api_key: str) -> dict:
    ...
```

> La firma `get_weather(city, api_key)` no cambia — `api_key` sigue siendo parámetro para facilitar el testing sin necesidad de manipular variables de entorno.

Concepto aplicado: sección 1 (logging) y sección 5 (retry) de `01_conceptos.md`.

---

### Paso 5 — Actualizar `demo_proyecto.py`

En `scripts/clase_03/demo_proyecto.py`, reemplaza cualquier uso de `os.getenv()` o `dotenv` por la instancia de `Settings`:

```python
from pycommute.config import get_settings

settings = get_settings()

# Usar settings.openweather_api_key y settings.openrouteservice_api_key
# en lugar de os.getenv(...)
```

El script debe arrancar, instanciar `Settings` (fail-fast si falta alguna key) y ejecutar la demo del proyecto.

---

### Paso 6 — Verificar los tests en verde

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run pytest tests/ -v
```

Todos los tests existentes deben pasar sin modificación. Si alguno falla por el cambio de `os.getenv` a `Settings`, revisa que `weather.py` aún recibe `api_key` como parámetro (paso 4) — los tests no deben depender de variables de entorno reales.

---

## ✅ Hito de la Clase 3

Tu código al terminar debe verse como `snapshots/clase_03/`.

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run python scripts/clase_03/demo_proyecto.py
```

Salida esperada (con configuración correcta):

```
2024-01-15 10:23:45 | INFO     | pycommute.weather | Consultando clima para Valencia
2024-01-15 10:23:46 | INFO     | pycommute.weather | Clima obtenido: 13°C, clear sky
```

Salida esperada (con API key faltante en `.env`):

```
ValidationError: 1 validation error for Settings
openweather_api_key: Field required
```

Si ves ambas salidas según corresponda, el hito está completo. Compara tu `src/pycommute/` con `snapshots/clase_03/src/pycommute/` para verificar que la estructura y los patrones aplicados coinciden.
