# Conceptos — Clase 01: El Setup Profesional

Cinco conceptos que usarás en cada clase del curso.
Cada sección tiene un ejemplo que puedes copiar y ejecutar por tu cuenta.

---

## 1. UV — El gestor de entornos moderno

### ¿Qué problema resuelve?

El flujo clásico de Python tiene demasiados pasos:

```bash
python -m venv .venv
source .venv/bin/activate   # o .venv\Scripts\activate en Windows
pip install httpx
pip freeze > requirements.txt
```

El problema: `requirements.txt` no garantiza que dos instalaciones produzcan
exactamente el mismo entorno. Un paquete que hoy instala la versión `1.2.3`
puede instalar `1.2.4` mañana en otra máquina.

`uv` reemplaza todo eso con tres comandos:

```bash
uv sync          # instala todo lo que define pyproject.toml (reproducible)
uv add httpx     # agrega una dependencia y actualiza el lock file
uv run pytest    # ejecuta un comando sin activar el entorno
```

### El lock file

Cuando ejecutas `uv add httpx`, `uv` crea (o actualiza) `uv.lock` con las
versiones exactas de `httpx` y todas sus dependencias. Ese archivo se versiona
en git. Resultado: todos en el proyecto instalan **exactamente** las mismas versiones.

### Pruébalo

```bash
# Windows (PowerShell) y Linux (idéntico)
mkdir mi-prueba
cd mi-prueba
uv init
uv add httpx
uv run python -c "import httpx; print(httpx.__version__)"
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_01/conceptos/01_uv_demo.py`

---

## 2. Src Layout — La estructura estándar de un paquete Python

### ¿Qué es?

Src layout es una convención donde el código del paquete vive dentro de `src/`:

```
mi-proyecto/
├── src/
│   └── mipaquete/        ← aquí vive el código
│       └── __init__.py
├── tests/
│   └── test_algo.py
└── pyproject.toml
```

### ¿Por qué no poner el paquete en la raíz?

Si el paquete está en la raíz (`mi-proyecto/mipaquete/`), cuando ejecutas
`pytest` desde `mi-proyecto/`, Python puede importar el paquete directamente
del disco en lugar del paquete instalado. Esto puede ocultar errores de
instalación que solo aparecerían en otro equipo o en producción.

Con src layout, `import mipaquete` solo funciona si el paquete está
correctamente instalado. Eso garantiza paridad entre tu entorno local y producción.

### Pruébalo

```bash
# Windows (PowerShell) y Linux (idéntico)
mkdir -p src/mipaquete
```

```python
# src/mipaquete/__init__.py
__version__ = "0.1.0"
```

Con un `pyproject.toml` que tenga `packages = ["src/mipaquete"]`:

```bash
# Windows (PowerShell) y Linux (idéntico)
uv sync
uv run python -c "import mipaquete; print(mipaquete.__version__)"
# 0.1.0
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_01/conceptos/02_src_layout_demo.py`

---

## 3. httpx — El cliente HTTP moderno

### ¿Qué hace httpx?

`httpx` es una librería para hacer peticiones HTTP. La usamos para hablar
con APIs externas que devuelven datos en formato JSON.

### El ejemplo mínimo

```python
import httpx

with httpx.Client() as client:
    response = client.get("https://httpbin.org/json")
    response.raise_for_status()   # lanza excepción si hay error (404, 500...)
    data = response.json()        # convierte la respuesta JSON a dict

print(data)
```

El `with httpx.Client() as client:` (context manager) garantiza que la
conexión se cierra correctamente aunque ocurra un error.

### ¿Por qué httpx y no requests?

`requests` es la librería más conocida y funciona bien para el caso síncrono.
`httpx` añade:

- Soporte para llamadas **asíncronas** nativo (`AsyncClient`)
- Timeouts explícitos por defecto (requests no tiene timeout por defecto)
- La misma API para modo sync y async: aprender uno sirve para los dos

### Pruébalo

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run python -c "
import httpx
with httpx.Client() as client:
    r = client.get('https://httpbin.org/get')
    print(r.json()['url'])
"
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_01/conceptos/03_httpx_demo.py`

---

## 4. Type Hints — Tipos en Python

### ¿Qué son?

Los type hints son anotaciones que indican qué tipo de dato acepta una función
y qué tipo devuelve:

```python
# Sin type hints — ¿qué acepta? ¿qué devuelve?
def process(data, limit):
    ...

# Con type hints — queda claro de un vistazo
def process(data: list[str], limit: int) -> dict[str, int]:
    ...
```

### ¿Para qué sirven?

**1. El IDE te ayuda más:**
```python
result = process(["a", "b"], 10)
result.  # el IDE sabe que result es dict[str, int] → sugiere .keys(), .values()...
```

**2. Detectan errores antes de ejecutar:**
```python
def greet(name: str) -> str:
    return f"Hola {name}"

greet(42)  # mypy avisa: Argument 1 has incompatible type "int"; expected "str"
```

**3. Documentación que no puede desincronizarse:**
El tipo en la firma siempre describe lo que acepta la función.

### Sintaxis básica

```python
# Tipos simples
def suma(a: int, b: int) -> int:
    return a + b

# Listas y diccionarios
def promedio(numeros: list[float]) -> float:
    return sum(numeros) / len(numeros)

# Valor opcional (puede ser str o None)
def buscar(nombre: str) -> str | None:
    ...

# Sin valor de retorno
def configurar() -> None:
    ...
```

### Importante: no son validación en runtime

```python
def suma(a: int, b: int) -> int:
    return a + b

# Python NO lanza error aunque los tipos sean incorrectos:
suma("hola", "mundo")  # devuelve "holamundo" sin quejarse
```

Los type hints los comprueban herramientas externas (`mypy`, el IDE),
no el intérprete de Python. Para validación en runtime se usa Pydantic.

### Pruébalo

```python
def describe_temperature(temp: float, unit: str) -> str:
    return f"{temp:.1f}°{unit}"

result: str = describe_temperature(24.5, "C")
print(result)  # 24.5°C
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_01/conceptos/04_type_hints_demo.py`

---

## 5. Variables de Entorno y `.env` — Gestión de secretos

### El problema

Una API key es una contraseña. Si la escribes en el código y haces commit,
queda expuesta en el historial de git para siempre:

```python
# ❌ Nunca hagas esto
API_KEY = "sk-abc123xyz789..."
```

### La solución: archivo `.env`

Crea un archivo `.env` en la raíz del proyecto (nunca lo versiones en git):

```env
API_KEY=tu_key_aqui
APP_ENV=development
```

Luego léelo desde Python con `python-dotenv`:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # carga las variables de .env al entorno

api_key = os.getenv("API_KEY")
print(api_key)  # tu_key_aqui
```

### El patrón `.env` / `.env.example`

```
.env          ← secrets reales — NUNCA lo subas a git (en .gitignore)
.env.example  ← plantilla con valores ficticios — SÍ se sube a git
```

Cuando alguien clona el proyecto:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env
# editar .env con las keys reales

# Linux
cp .env.example .env
# editar .env con las keys reales
```

### Pruébalo

```bash
# Windows (PowerShell) y Linux (idéntico)
echo "APP_NAME=MiApp" > .env
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("APP_NAME"))  # MiApp
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_01/conceptos/05_dotenv_demo.py`
