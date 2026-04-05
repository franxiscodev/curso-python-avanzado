# Clase 00 — Setup Profesional

Antes de escribir una sola línea de PyCommute necesitas un entorno
que funcione igual en tu máquina y en producción. Esta clase lo construye
paso a paso.

**Hito verificable al final:**

```bash
uv run pytest tests/ -q
# 57 passed
```

---

## Bloque 1 — UV + Python 3.12

### Instalar UV

```bash
# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Recargar PATH en la misma sesión
source $HOME/.local/bin/env
```

### Verificar e instalar Python 3.12

```bash
# Verificar UV
uv --version   # 0.4.x o superior

# Instalar Python 3.12 con UV
uv python install 3.12

# Verificar
uv python list  # debe mostrar cpython-3.12.x disponible
```

### Por qué UV y no pip

| pip + venv | UV |
|------------|-----|
| `python -m venv .venv` | `uv init` |
| `source .venv/bin/activate` | `uv run` (sin activar) |
| `pip install paquete` | `uv add paquete` |
| `requirements.txt` manual | `pyproject.toml` automático |
| Lento | 10-100x más rápido (escrito en Rust) |

En este curso **no usamos pip ni requirements.txt**.
Todo es UV y `pyproject.toml`.

UV también gestiona versiones de Python — no necesitas pyenv, conda
ni instalar Python manualmente.

---

## Bloque 2 — VS Code + Extensiones + Ruff

### Instalar extensiones

```bash
# Linux
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension tamasfe.even-better-toml
code --install-extension mhutchie.git-graph
```

### Por qué cada extensión

- **Python + Pylance** — motor de inteligencia del IDE, autocompletado y detección de errores
- **Ruff** — linter y formateador. Reemplaza flake8, isort, black y pylint en una sola herramienta
- **Even Better TOML** — syntax highlighting para `pyproject.toml`, lo abrirás en cada clase
- **Git Graph** — árbol visual del historial de git en el IDE

### Configurar Ruff como formateador

Abre `Ctrl+Shift+P` → **Open User Settings (JSON)** y añade:

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    }
}
```

Prueba en vivo: escribe imports desordenados → guarda → Ruff los reordena automáticamente.

---

## Bloque 3 — Git + GitHub + SSH Key

### Configuración inicial de Git

```bash
# Linux
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
git config --global init.defaultBranch main
git config --list
```

### Generar SSH key y conectar con GitHub

```bash
# Linux
# Generar key (ed25519 es el algoritmo recomendado)
ssh-keygen -t ed25519 -C "tu@email.com"

# Mostrar la clave pública
cat ~/.ssh/id_ed25519.pub
# Copiar el output → github.com → Settings → SSH and GPG keys → New SSH key
```

Verificar la conexión:

```bash
ssh -T git@github.com
# "Hi tu_usuario! You've successfully authenticated..."
```

### Si no tienes cuenta GitHub

1. Ir a github.com → Sign Up
2. Verificar el email
3. Plan gratuito es suficiente para todo el curso

### Por qué SSH y no HTTPS

HTTPS pide credenciales en cada operación. SSH usa la key generada
una vez y funciona sin interrupciones. Para un curso con muchos commits
por sesión, SSH es la opción correcta.

---

## Bloque 4 — API Keys + Gestión de Secretos

### El problema: secretos en git

Primero vemos qué pasa si no gestionamos bien los secretos:

```bash
# Linux
mkdir ~/demo-secretos && cd ~/demo-secretos
git init
echo "MI_API_KEY=sk-abc123supersecreto" > config.txt
git add config.txt
git commit -m "agregando configuracion"
# Si pusheamos a GitHub → la key queda visible para todo el mundo
```

Las API keys filtradas en GitHub son uno de los vectores de ataque más comunes.

### La solución correcta

```bash
# Linux — crear el .gitignore ANTES del primer commit
cat > .gitignore << 'EOF'
.venv/
.env
__pycache__/
*.log
*.pyc
.pytest_cache/
.ruff_cache/
EOF

# El archivo real — NUNCA a git
cat > .env << 'EOF'
OPENWEATHER_API_KEY=
OPENROUTESERVICE_API_KEY=
GOOGLE_API_KEY=
EOF

# La plantilla pública — SÍ a git
cp .env .env.example

git add .gitignore .env.example
git status  # .env NO debe aparecer en la lista
```

**Regla de oro:**
```
.env         → NUNCA a git, NUNCA compartir
.env.example → SIEMPRE a git, sin valores reales
```

### Cómo obtener las API keys

**OpenWeatherMap** — openweathermap.org → Sign Up → My API Keys → Generate
> Puede tardar hasta 2 horas en activarse la primera vez.

**OpenRouteService** — openrouteservice.org → Sign Up → Dashboard → Request a token
> Activo inmediatamente.

**Google AI Studio (se usa en Clase 10)** — aistudio.google.com → Get API Key
> Activo inmediatamente.

---

## Bloque A — Construir desde cero con UV

### Iniciar el proyecto

```bash
# Linux
cd ~
uv init --lib hola-pycommute
cd hola-pycommute
```

UV genera en 0.3 segundos:

```
hola-pycommute/
├── src/
│   └── hola_pycommute/
│       ├── __init__.py
│       └── py.typed
├── pyproject.toml
├── README.md
└── .python-version
```

### Por qué `--lib` y src layout

`--lib` activa el src layout automáticamente.

```
Sin src layout:          Con src layout (--lib):
proyecto/                proyecto/
├── weather.py           ├── src/
├── tests/               │   └── hola_pycommute/
│   └── test.py          │       └── weather.py
└── main.py              └── tests/
                              └── test_weather.py
```

Sin src layout, Python importa el código sin instalarlo — esto oculta
errores de packaging que explotan en producción.

El paquete usa guión bajo: `hola-pycommute` (nombre del proyecto)
→ `hola_pycommute` (nombre del import en Python).

### Agregar dependencias

```bash
# Linux
uv add httpx python-dotenv
uv add --dev pytest ruff
cat pyproject.toml  # ver el resultado
```

### Crear .gitignore y .env antes del primer commit

```bash
# Linux
cat > .gitignore << 'EOF'
.venv/
.env
__pycache__/
*.log
*.pyc
.pytest_cache/
.ruff_cache/
EOF

cat > .env << 'EOF'
OPENWEATHER_API_KEY=
EOF

cat > .env.example << 'EOF'
OPENWEATHER_API_KEY=
EOF
```

### El código del cliente de clima

**`src/hola_pycommute/weather.py`:**

```python
"""Cliente de clima — primera llamada real a OpenWeather API."""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str) -> dict:
    """Obtiene el clima actual de una ciudad.

    Args:
        city: Nombre de la ciudad.

    Returns:
        Dict con temperature, description y city.

    Raises:
        ValueError: Si la API key no esta configurada.
        httpx.HTTPError: Si la API devuelve un error.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY no esta configurada en .env")

    response = httpx.get(
        BASE_URL,
        params={"q": city, "appid": api_key, "units": "metric"},
    )
    response.raise_for_status()
    data = response.json()

    return {
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "city": data["name"],
    }
```

**`tests/test_weather.py`:**

```python
"""Tests del cliente de clima."""
import pytest
from hola_pycommute.weather import get_weather


def test_get_weather_raises_without_key(monkeypatch):
    """Verifica el manejo de API key faltante — no requiere internet."""
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENWEATHER_API_KEY"):
        get_weather("Valencia")
```

### El workflow completo

```bash
# Linux
# 1. Ruff antes de commitear — siempre
uv run ruff check src/

# 2. Tests
uv run pytest tests/ -v

# 3. Primer commit
git init
git add .gitignore .env.example pyproject.toml uv.lock README.md src/ tests/
git status  # verificar que .env NO aparece
git commit -m "feat: primer cliente de clima con src layout"

# 4. Pushear a GitHub
git remote add origin git@github.com:TU_USUARIO/hola-pycommute.git
git push -u origin main
```

### Verificar Docker y Ollama

> ℹ️ **Preinstalado por el instructor:** Docker y Ollama ya están
> disponibles en la VM. Solo verificamos que funcionan.

```bash
# Linux
# Docker
docker run hello-world
docker pull python:3.12-slim  # anticipa Clase 13

# Ollama
ollama list              # debe mostrar gemma3:1b
ollama run gemma3:1b "Saluda en español en una sola palabra"
# Respuesta esperada: "Hola"
```

---

## Bloque B — Clonar PyCommute Elite

```bash
# Linux
cd ~
git clone git@github.com:franxiscodev/pycommute-elite-publico.git
cd pycommute-elite-publico

# Configurar entorno
cp .env.example .env
# Completar con las API keys cuando las tengas

# Instalar dependencias
uv sync

# Explorar la estructura
ls -la
cat pyproject.toml
```

### El hito de la clase

```bash
# Linux
uv run pytest tests/ -q
```

Resultado esperado:

```
57 passed in X.XXs
```

### Verificar tu entorno completo

El script `verificar_entorno.py` comprueba automáticamente todas las
herramientas instaladas:

```bash
# Linux
uv run python verificar_entorno.py
```

Resultado esperado:

```
=== Verificacion del entorno PyCommute ===

  [OK] Python 3.12 — 3.12.x
  [OK] UV instalado — /home/usuario/.local/bin/uv
  [OK] Git configurado — Tu Nombre
  [OK] SSH GitHub — OK
  [OK] Docker — Docker version 27.x
  [OK] Docker sin sudo — OK
  [OK] Ollama — OK
  [OK] Modelo gemma3:1b — disponible
  [OK] VS Code
  [OK] Repo PyCommute clonado — /home/usuario/pycommute-elite-publico
  [OK] 57 tests en verde — 57 passed

========================================
  11/11 verificaciones pasadas
  Entorno listo para Clase 1
```
