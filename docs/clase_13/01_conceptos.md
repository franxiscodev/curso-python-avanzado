# Clase 13 — Deploy y CI/CD: Docker Compose + GitHub Actions

## ¿Qué es Docker?

Docker permite empaquetar una aplicación con todo lo que necesita para
ejecutarse: el sistema operativo base, Python, las dependencias y el código.

Ese paquete se llama **imagen**. Al ejecutarla, se crea un **contenedor**.

```
Imagen Docker  ←→  Receta de cocina
Contenedor     ←→  El plato preparado

La misma receta produce el mismo plato en cualquier cocina del mundo.
```

**El problema que resuelve:**

```
Sin Docker:
  Tu máquina:     Python 3.12, httpx 0.27, variable X=abc → funciona
  Máquina de CI:  Python 3.11, httpx 0.26, variable X no definida → falla

Con Docker:
  El contenedor lleva TODO — Python, deps, variables → igual en todas partes
```

**Contenedor vs Máquina Virtual:**

```
Máquina Virtual:          Contenedor:
  Host OS                   Host OS
  └── Hypervisor            └── Docker Engine (comparte kernel)
      └── Guest OS completo     └── Solo tu app + sus deps
          └── Tu app

VM: mayor aislamiento, más pesada (GB, minutos de arranque)
Contenedor: suficiente aislamiento, más ligero (MB, segundos de arranque)
```

---

## Dockerfile — instrucciones para construir la imagen

El `Dockerfile` es una lista de instrucciones para construir la imagen.
Cada instrucción crea una **capa**. Docker cachea cada capa.

```dockerfile
# Imagen base — Python 3.12 mínimo
FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar UV (nuestro gestor de dependencias)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copiar deps PRIMERO (aprovecha el cache de Docker)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copiar código fuente DESPUÉS
COPY src ./src

# Puerto de la app
EXPOSE 8000

# Comando de arranque
CMD ["uv", "run", "uvicorn", "mi_app.main:app",
     "--host", "0.0.0.0", "--port", "8000"]
```

**La regla del cache — por qué el orden importa:**

```
MALO — deps se reinstalan en cada build:
  COPY . .                     ← todo junto
  RUN uv sync --frozen

BUENO — deps se cachean:
  COPY pyproject.toml uv.lock ./ ← deps primero (cambian poco)
  RUN uv sync --frozen            ← cacheado si deps no cambian
  COPY src ./src                  ← código (cambia frecuente)
```

Con el orden correcto, cambiar el código no invalida el cache de dependencias.
El build pasa de minutos a segundos.

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_13/conceptos/02_dockerfile_explicado.py`

---

## Docker Compose — orquestar múltiples servicios

Un `Dockerfile` define cómo construir una imagen.
`docker-compose.yml` define cómo ejecutar varios servicios juntos.

```yaml
services:

  mi-app:
    build: .               # construir desde Dockerfile
    ports:
      - "8000:8000"        # host:contenedor
    environment:
      - API_KEY=${API_KEY} # leer de .env del host
      - DB_URL=http://base-de-datos:5432
      #                              ^^^^^^^^^^^^^^^
      #                              nombre del servicio = hostname

  base-de-datos:
    image: postgres:16     # imagen pública de Docker Hub
    volumes:
      - db_data:/var/lib/postgresql/data  # persistir datos

volumes:
  db_data:
```

**Networking interno — el concepto más importante:**

```
Docker Compose crea una red privada para todos los servicios.
Dentro de esa red, cada servicio es accesible por su nombre.

Sin Compose:  DB_URL=http://localhost:5432
Con Compose:  DB_URL=http://base-de-datos:5432
                                ^^^^^^^^^^^^
                                nombre del servicio en el compose
```

El código no cambia — solo el valor de la variable de entorno.

**Comandos esenciales:**

```bash
docker compose up --build   # primera vez o cuando cambia el código
docker compose up           # veces siguientes (sin rebuild)
docker compose down         # detener y eliminar contenedores
docker compose logs api     # ver logs de un servicio
docker compose ps           # ver estado de los servicios
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_13/conceptos/01_docker_conceptos.py`
  `uv run scripts/clase_13/conceptos/03_compose_explicado.py`

---

## Variables de entorno en Docker

Hay tres formas de pasar variables de entorno a un contenedor:

```yaml
environment:
  # 1. Leer del .env del host (recomendado para secretos)
  - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}

  # 2. Valor fijo en el compose
  - APP_ENV=production

  # 3. Con valor por defecto si no está en .env
  - OLLAMA_MODEL=${OLLAMA_MODEL:-gemma3:1b}
```

**Regla de oro de seguridad:**
- El archivo `.env` con claves reales va en `.gitignore` — nunca al repo
- `.env.example` sí va al repo — muestra el formato sin valores reales
- En CI, las keys de prueba van directamente en el workflow (los tests usan mocks)
- En producción, usar los Secrets de la plataforma (GitHub Secrets, AWS Secrets Manager)

---

## GitHub Actions — CI automatizado

GitHub Actions ejecuta código automáticamente cuando ocurre un evento
(push, PR, etc.) en tu repositorio.

**Estructura de un workflow:**

```
.github/
└── workflows/
    └── ci.yml          ← el archivo de configuración

ci.yml
├── name: nombre del workflow
├── on: cuándo ejecutarlo (push, PR, etc.)
└── jobs:
    └── nombre-del-job:
        ├── runs-on: ubuntu-latest   ← VM de GitHub
        └── steps:
            ├── uses: acción predefinida
            └── run: comando shell
```

**Un workflow de CI mínimo:**

```yaml
name: CI
on:
  push:
    branches: [main]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      # descargar el código
      - uses: astral-sh/setup-uv@v3    # instalar UV
      - run: uv sync --all-extras      # instalar dependencias
      - run: uv run pytest tests/ -v   # correr tests
```

**Resultado visible en GitHub:**

```
git push → GitHub detecta el push → crea VM limpia
→ ejecuta steps → resultado:
  ✅ check verde — todo OK
  ❌ check rojo  — algo falló → notificación al developer
```

**`uses:` vs `run:`:**

```yaml
# uses: ejecuta una Action predefinida (código reutilizable de la comunidad)
- uses: actions/checkout@v4

# run: ejecuta un comando shell normal (igual que en tu terminal)
- run: uv run pytest tests/ -v
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_13/conceptos/04_github_actions_explicado.py`
