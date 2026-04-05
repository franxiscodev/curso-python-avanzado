# Conceptos — Clase 01: El Setup Profesional

Cinco herramientas que usarás en cada clase del curso.
Esta sección explica qué hace cada una, por qué existe y cómo usarla.

---

## 1. El stack del curso — por qué estas cinco herramientas

En Python hay decenas de formas de instalar dependencias, hacer peticiones HTTP
o gestionar secretos. En este curso elegimos un conjunto específico y lo usamos
de forma consistente desde la Clase 1.

### Las cinco piezas

| Herramienta | Qué hace | Por qué la elegimos |
|-------------|----------|---------------------|
| `uv` | Gestiona entornos virtuales y dependencias | Reproducibilidad garantizada via lock file |
| Src layout | Estructura del paquete | Evita importar código roto sin saberlo |
| `httpx` | Cliente HTTP | Soporta sync y async con la misma API |
| Type hints | Anotaciones de tipos | El IDE ayuda más; mypy detecta errores antes |
| `python-dotenv` | Lee archivos `.env` | Mantiene los secretos fuera del código |

### Cómo encajan

El flujo completo de la aplicación que construiremos:

```
.env ──► python-dotenv ──► os.getenv("API_KEY")
                                  │
                              httpx.Client
                                  │
                              JSON response
                                  │
                          funciones con type hints
```

Cada herramienta tiene un rol preciso. Si falta una, aparece un problema concreto:
sin `uv`, el entorno no es reproducible; sin type hints, el IDE no puede ayudarte;
sin `.env`, la key queda expuesta en git para siempre.

---

## 2. UV — Entorno aislado y reproducible

### El problema que resuelve

El flujo clásico tiene dos problemas:

**1. Demasiados pasos:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install httpx
pip freeze > requirements.txt
```

**2. `requirements.txt` no garantiza reproducibilidad:**
`pip install -r requirements.txt` hoy puede instalar `httpx==0.27.2`
y mañana en otra máquina instalar `httpx==0.28.0`. El código puede romperse
sin que nadie cambie nada.

### La solución: lock file

`uv` usa un archivo `uv.lock` que registra las versiones exactas con hashes:

```toml
[[package]]
name = "httpx"
version = "0.27.2"
[[package.metadata.files]]
name = "httpx-0.27.2-py3-none-any.whl"
hash = "sha256:a8d9..."
```

El hash garantiza que si alguien modifica el paquete en PyPI, `uv sync` detecta
la diferencia y falla — en lugar de instalar silenciosamente algo distinto.

### Los tres comandos que usarás siempre

```bash
# Windows (PowerShell) y Linux (idéntico)
uv sync                          # instala todo lo que define pyproject.toml
uv add httpx                     # agrega dependencia y actualiza uv.lock
uv run python scripts/...        # ejecuta sin activar el entorno manualmente
```

### Qué verifica el script

`01_uv_demo.py` comprueba si `sys.prefix != sys.base_prefix`.
Cuando difieren, el intérprete activo es el del entorno virtual, no el del sistema.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_01/conceptos/01_uv_demo.py`

### Analiza la salida

```
¿Entorno aislado?: True
Ruta activa: C:\...\pycommute-elite\curso\.venv
```

- `True` confirma que estás dentro del entorno de `uv`.
- La ruta apunta a `.venv/` dentro del proyecto, no al Python del sistema.
- Si ves `False`, ejecuta `uv sync` desde la carpeta `curso/`.

---

## 3. Src Layout — El paquete solo existe si está instalado

### El problema que resuelve

Si el paquete está en la raíz del proyecto:

```
proyecto/
├── mipaquete/    ← aquí
│   └── __init__.py
└── tests/
```

Cuando ejecutas `pytest` desde `proyecto/`, Python añade `proyecto/` a `sys.path`.
`import mipaquete` encuentra el paquete **directamente en el disco**, sin instalarlo.

Consecuencia: si `pyproject.toml` tiene un error que impide la instalación, los tests
siguen pasando en tu máquina. En CI (donde el paquete se instala desde cero), fallan.

### La solución: mover el código a `src/`

```
proyecto/
├── src/
│   └── mipaquete/    ← aquí
│       └── __init__.py
└── tests/
```

`src/` no está en `sys.path` por defecto. `import mipaquete` solo funciona si el
paquete está instalado. Esto fuerza paridad entre tu entorno local y producción.

Cuando ejecutas `uv sync`, `uv` crea un archivo `.pth` en el entorno:

```
# .venv/lib/python3.12/site-packages/pycommute.pth
/ruta/absoluta/proyecto/src
```

Este `.pth` añade `src/` al path al iniciar Python — sin necesidad de reconstruir
el paquete en cada cambio de código.

### Qué verifica el script

`02_src_layout_demo.py` comprueba si el directorio actual está en `sys.path`.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_01/conceptos/02_src_layout_demo.py`

### Analiza la salida

```
¿Directorio actual expuesto en sys.path?: False
En un flat-layout esto sería True. Con src-layout, es mitigado.
```

- `False` confirma que el directorio de trabajo no está expuesto directamente.
- Con flat-layout (paquete en la raíz) verías `True`, y el riesgo de import
  shadowing estaría activo.

---

## 4. httpx — Cliente HTTP con control de errores

### El problema que resuelve

Una llamada HTTP puede fallar de tres formas distintas:

| Tipo de fallo | Qué ocurre | Excepción |
|---------------|------------|-----------|
| Error del servidor | La API devuelve 4xx/5xx | `HTTPStatusError` |
| Red interrumpida | No hay respuesta | `RequestError` |
| API lenta | El servidor tarda demasiado | `TimeoutException` |

`requests` no tiene timeout por defecto — una llamada sin respuesta puede
bloquear el hilo indefinidamente. `httpx` tiene timeout de 5s por defecto,
y permite configurarlo con precisión.

### El patrón con context manager

```python
import httpx

with httpx.Client(timeout=3.0) as client:
    response = client.get("https://api.ejemplo.com/datos")
    response.raise_for_status()   # convierte 4xx/5xx en excepción
    data = response.json()        # solo llega aquí si el código fue 2xx
```

`with httpx.Client() as client:` garantiza que el pool de conexiones se cierra
correctamente aunque ocurra un error.

### Los tres escenarios del script

`03_httpx_demo.py` demuestra los tres casos con `httpbin.org`:
- **Escenario 1** (`/status/200`): la llamada exitosa — verifica que el "camino feliz" funciona.
- **Escenario 2** (`/status/404`): el servidor devuelve error — `raise_for_status()` lo convierte en `HTTPStatusError`.
- **Escenario 3** (`/delay/5`): el servidor tarda 5s pero el cliente tiene timeout de 3s — se lanza `TimeoutException`.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_01/conceptos/03_httpx_demo.py`

### Analiza la salida

```
[*] ESCENARIO 1: El Camino Feliz (200 OK)
    [OK] Exito absoluto. Codigo de estado: 200

[*] ESCENARIO 2: Fallo del Servidor (404 Not Found)
    [CONTROLADO] El servidor rechazo la peticion con codigo 404

[*] ESCENARIO 3: La API se queda colgada (Timeout)
    [TIMEOUT] La API tardo demasiado. El cliente corto la conexion para salvar el hilo.
```

Cada escenario tiene su excepción específica — el código nunca llega a un estado
desconocido. En la Clase 3 añadiremos `@retry` para reintentar automáticamente
en los escenarios 2 y 3.

---

## 5. Type Hints — TypedDict y Literal

### El problema que resuelven

Sin type hints, un dict es opaco:

```python
def analyze_route(route):
    mode = route["transport_mode"]  # ¿qué valores acepta? no se sabe
```

Con `TypedDict` y `Literal`, el contrato queda explícito en el código:

```python
from typing import TypedDict, Literal

class CommuteRoute(TypedDict):
    origin: str
    destination: str
    distance_km: float
    transport_mode: Literal["driving", "walking", "transit"]
```

Ahora el IDE autocompletea las claves y mypy rechaza valores fuera del conjunto
de `Literal` antes de ejecutar el código.

### TypedDict — la forma exacta de un diccionario

`TypedDict` define qué claves tiene un diccionario y qué tipo tiene cada una.
A diferencia de `dict[str, Any]`, el IDE sabe exactamente qué esperar:

```python
route: CommuteRoute = {
    "origin": "Casa",
    "destination": "Oficina",
    "distance_km": 2.5,
    "transport_mode": "walking"   # mypy acepta solo los 3 valores del Literal
}
```

### Literal — valores permitidos, no tipos genéricos

`Literal["driving", "walking", "transit"]` es más restrictivo que `str`.
mypy rechaza cualquier valor que no esté en la lista:

```python
# Esto hace explotar mypy:
route["transport_mode"] = "flying"  # error: "flying" no está en el Literal
```

### Los tipos no validan en runtime

```python
route["transport_mode"] = "flying"   # Python NO lanza error en ejecución
```

Los type hints son para herramientas estáticas (IDE, mypy). Para validación
en runtime se usa Pydantic — lo veremos en la Clase 8.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_01/conceptos/04_type_hints_demo.py`

### Analiza la salida

```
Ruta viable usando walking.
```

El script ejecuta `analyze_route(valid_route)`. Descomenta el bloque `invalid_route`
al final y ejecuta `mypy scripts/clase_01/conceptos/04_type_hints_demo.py` para ver
cómo mypy detecta los dos problemas (campo faltante y valor fuera del Literal).

---

## 6. Variables de entorno y `.env` — Gestión segura de secretos

### El problema que resuelve

Una API key es una contraseña. Si la escribes en el código:

```python
# Nunca hagas esto
API_KEY = "sk-abc123xyz789..."
```

Queda expuesta en el historial de git para siempre, aunque la borres después.
Recuperarla requiere reescribir el historial (`git filter-repo`), lo que
afecta a todos los colaboradores.

### La solución: archivo `.env`

```env
# .env  —  nunca lo subas a git
API_KEY=sk-live-123456789
APP_ENV=produccion
```

```python
import os
from dotenv import load_dotenv

load_dotenv()                          # inyecta .env en os.environ
api_key = os.getenv("API_KEY")         # str | None
entorno = os.getenv("APP_ENV", "dev")  # con valor por defecto
```

### El patrón `.env` / `.env.example`

```
.env          ← secrets reales — NUNCA en git (.gitignore)
.env.example  ← plantilla con valores ficticios — SÍ en git
```

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux
cp .env.example .env
```

Un desarrollador nuevo puede levantar el proyecto en minutos:
el `.env.example` documenta exactamente qué variables se necesitan.

### Qué demuestra el script

`05_dotenv_demo.py` crea un `.env.local` temporal, lo inyecta con `load_dotenv`,
lee los valores, enmascara la key para el log y borra el archivo en el bloque `finally`.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_01/conceptos/05_dotenv_demo.py`

### Analiza la salida

```
[*] Creando archivo .env.local en disco...
[*] El archivo se creará en: C:\...\pycommute-elite\curso\.env.local
[*] Secretos inyectados en memoria.

[ENV] Entorno activo: produccion
[KEY] API Key cargada: sk-live...789

[*] Limpieza: .env.local eliminado del disco.
```

- `finally` garantiza que el archivo se borra incluso si el código anterior lanza una excepción.
- La key aparece como `sk-live...789` — nunca se loguea completa.
- En la Clase 3 reemplazamos `os.getenv` por `pydantic-settings`, que valida los tipos
  y falla en startup si falta una variable obligatoria.
