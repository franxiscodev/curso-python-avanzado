# Lab — Clase 13: Docker Compose + GitHub Actions

## Objetivo

Empaquetar PyCommute en Docker Compose y configurar un pipeline de CI
que verifica automáticamente lint y tests en cada push.

Al finalizar este lab:
- `docker compose up --build` arranca el sistema completo
- Cualquier push a `main` ejecuta los tests en GitHub automáticamente

## Prerrequisitos

- Clase 12 completada — API FastAPI funcionando
- Docker instalado y corriendo
- Repositorio en GitHub (para el paso de GitHub Actions)

No hay dependencias Python nuevas en esta clase.

---

## Paso 1 — Dockerfile

Crea `Dockerfile` en el directorio `curso/`.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Dependencias primero — aprovecha el cache de Docker
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Código fuente después
COPY src ./src

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "pycommute.api.main:app",
     "--host", "0.0.0.0", "--port", "8000"]
```

Aplica: sección "Dockerfile" de `01_conceptos.md`.

---

## Paso 2 — docker-compose.yml

Crea `docker-compose.yml` en el directorio `curso/`.

```yaml
services:

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - OPENROUTESERVICE_API_KEY=${OPENROUTESERVICE_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=${OLLAMA_MODEL:-gemma3:1b}
      - APP_ENV=production
      - LOG_LEVEL=INFO
    depends_on:
      - ollama
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

Aplica: sección "Docker Compose" de `01_conceptos.md`.

---

## Paso 3 — .dockerignore

Crea `.dockerignore` en `curso/`:

```
.venv/
.env
__pycache__/
*.pyc
.pytest_cache/
snapshots/
docs/
scripts/
*.md
.git/
tests/
```

---

## Paso 4 — Verificar que el servidor arranca

```bash
# Windows (PowerShell) — desde la raíz de tu repo
docker compose up --build

# Linux — desde la raíz de tu repo
docker compose up --build
```

La primera vez tarda más — Docker descarga las imágenes de Python y Ollama.
Las veces siguientes es mucho más rápido (cache de capas).

Cuando veas `Application startup complete.` en los logs, en otro terminal:

```bash
# Windows (PowerShell)
curl http://localhost:8000/health

# Linux
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{"status": "ok", "version": "0.1.0", "adapters": {...}}
```

También puedes abrir `http://localhost:8000/docs` en el browser.

---

## Paso 5 — GitHub Actions CI

Crea `.github/workflows/ci.yml` en la **raíz del repositorio** (no en `curso/`):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    name: Lint y Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout codigo
        uses: actions/checkout@v4

      - name: Instalar UV
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Instalar Python
        run: uv python install 3.12

      - name: Instalar dependencias
        run: uv sync --all-extras

      - name: Lint con ruff
        run: uv run ruff check src/

      - name: Tests con pytest
        run: uv run pytest tests/ -v --tb=short
        env:
          OPENWEATHER_API_KEY: "test-key"
          OPENROUTESERVICE_API_KEY: "test-key"
          GOOGLE_API_KEY: "test-key"
          OLLAMA_BASE_URL: "http://localhost:11434"
          OLLAMA_MODEL: "gemma3:1b"
```

Aplica: sección "GitHub Actions" de `01_conceptos.md`.

---

## Paso 6 — Hacer push y ver el check verde

```bash
# Windows y Linux — desde la raíz del repo
git add .github/workflows/ci.yml curso/Dockerfile curso/docker-compose.yml curso/.dockerignore
git commit -m "feat: Docker Compose + GitHub Actions CI"
git push origin main
```

Abre GitHub → tu repositorio → pestaña "Actions".
Verás el workflow ejecutándose. En 2-3 minutos aparece el check verde.

---

## Demo del sistema completo

```bash
# Windows (PowerShell) — desde la raíz del repo
uv run python curso/scripts/clase_13/demo_proyecto.py

# Linux — desde la raíz del repo
uv run python curso/scripts/clase_13/demo_proyecto.py
```

El script verifica si la API está corriendo en Docker y muestra el
estado completo del sistema.

---

## ¿Por qué esto es el cierre perfecto?

### La arquitectura hexagonal cumplió su promesa

En Clase 8 definimos una arquitectura donde agregar nuevas capas
no requería modificar el código existente.

En Clase 12 comprobamos que añadir FastAPI no tocó `core/` ni `adapters/`.

En Clase 13 comprobamos que añadir Docker no toca nada del código Python.
El `Dockerfile` envuelve lo que ya existe. `docker-compose.yml` orquesta
servicios sin saber cómo están implementados internamente.

Cada capa es independiente. Eso es diseño profesional.

### Docker garantiza reproducibilidad

```
Tu máquina → docker compose up → funciona
VM del alumno → docker compose up → funciona igual
Servidor en la nube → docker compose up → funciona igual
```

"En mi máquina funciona" deja de ser un problema.

### GitHub Actions garantiza calidad continua

Los 57 tests que escribimos desde Clase 4 ahora se ejecutan
automáticamente en cada push. Sin intervención manual.

El diseño con mocks de Clase 4 fue la razón por la que CI funciona
sin claves reales ni acceso a internet en los tests.

### El sistema completo

```
[Browser / curl]
      ↓ HTTP
[FastAPI :8000]  ← contenedor Docker
      ↓
[CommuteService]
  ↙        ↘         ↘
[Weather]  [Route]  [FallbackAI]
                      ↙        ↘
                 [Gemini]   [Ollama]  ← contenedor Docker
```

Construiste un sistema de IA híbrida con arquitectura hexagonal,
expuesto como API REST, empaquetado en Docker, con CI automatizado.

Eso es ingeniería de software profesional.

---

## Snapshot del hito final

El estado completo del proyecto está en:

```
snapshots/clase_13/src/pycommute/
snapshots/clase_13/tests/
snapshots/clase_13/Dockerfile
snapshots/clase_13/docker-compose.yml
```

Este snapshot es el proyecto terminado.
Es idéntico a `src/pycommute/` al cerrar la Clase 13.
