"""Dockerfile — cada instruccion explicada con su proposito.

Muestra el Dockerfile de PyCommute linea por linea con comentarios
detallados explicando que hace cada instruccion y por que.

Enfasis en:
- La regla de oro del cache: poner lo que cambia menos PRIMERO
- Por que usamos UV en lugar de pip
- Por que COPY deps antes que COPY src/

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_13/conceptos/02_dockerfile_explicado.py

    # Linux
    uv run scripts/clase_13/conceptos/02_dockerfile_explicado.py
"""

print("=== Dockerfile de PyCommute — cada linea explicada ===\n")

instrucciones = [
    (
        "FROM python:3.12-slim",
        "Imagen base",
        """python:3.12-slim = imagen oficial de Python en su version 'slim'.
    'slim' significa: solo lo minimo para correr Python, sin compiladores
    ni herramientas de desarrollo. Imagen resultante: ~130MB en vez de ~1GB.
    Siempre especificar version exacta (3.12) para reproducibilidad.""",
    ),
    (
        "WORKDIR /app",
        "Directorio de trabajo",
        """Crea /app si no existe y hace 'cd /app'.
    Todos los comandos siguientes (COPY, RUN, CMD) se ejecutan desde /app.
    Buena practica: usar /app como directorio raiz de la aplicacion.""",
    ),
    (
        "COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/",
        "Instalar UV",
        """Copia el binario de UV desde su imagen oficial en GitHub Container Registry.
    --from=<imagen>: Docker descarga esa imagen y copia archivos de ella.
    /uv y /uvx son los binarios de UV -> se copian a /bin/ del contenedor.
    Ventaja: sin pip, sin curl, sin dependencias adicionales.
    UV gestiona Python y las dependencias igual que en desarrollo.""",
    ),
    (
        "COPY pyproject.toml uv.lock ./",
        "Copiar archivos de dependencias",
        """Copiamos SOLO los archivos de dependencias, no el codigo fuente todavia.
    REGLA DE ORO del cache de Docker:
      Cada instruccion del Dockerfile crea una 'capa'.
      Docker cachea cada capa. Si una capa no cambia, Docker la reutiliza.
      Si una capa cambia, Docker invalida ESA y TODAS las capas siguientes.

    pyproject.toml y uv.lock cambian solo cuando agregas nuevas deps.
    src/ cambia en cada commit de codigo.

    Al copiar deps primero:
      -> Si solo cambia src/, Docker reutiliza la capa de instalacion de deps
      -> El build es mucho mas rapido (no reinstala todas las deps cada vez)""",
    ),
    (
        "RUN uv sync --frozen --no-install-project",
        "Instalar dependencias",
        """uv sync --frozen: instala EXACTAMENTE lo que dice uv.lock, sin actualizar.
    --no-install-project: instala las deps pero no el proyecto en si todavia.
    (Lo instalaremos despues de copiar el codigo fuente.)

    Este step tarda en la primera vez (descarga paquetes de PyPI).
    Las veces siguientes, si no cambiaron las deps, Docker reutiliza esta capa.""",
    ),
    (
        "COPY curso/src ./src",
        "Copiar codigo fuente",
        """Copiamos src/ DESPUES de instalar las deps.
    Por que? Por la regla del cache:
      - Cambiar src/ invalida esta capa y las siguientes
      - Pero NO invalida la capa de instalacion de deps (la anterior)
      - Docker reutiliza las deps -> el build es rapido aunque el codigo cambie

    Solo copiamos src/ — sin tests, docs, scripts ni snapshots.
    (El .dockerignore excluye el resto.)""",
    ),
    (
        "EXPOSE 8000",
        "Puerto de la app",
        """EXPOSE es documentacion — le dice a Docker que la app usa el puerto 8000.
    NO abre el puerto por si solo.
    El puerto se abre con:
      - docker run -p 8000:8000    (manual)
      - ports: en docker-compose.yml (con Compose)""",
    ),
    (
        'CMD ["uv", "run", "uvicorn", "pycommute.api.main:app", "--host", "0.0.0.0", "--port", "8000"]',
        "Comando de inicio",
        """CMD define el comando que ejecuta el contenedor al arrancar.
    Forma de lista (no string) para evitar que el shell interprete los argumentos.

    --host 0.0.0.0: acepta conexiones desde FUERA del contenedor.
      Sin esto, uvicorn escucharia en localhost (127.0.0.1) dentro del contenedor
      y ninguna peticion externa llegaria.
    --port 8000: el mismo que EXPOSE y que ports: en docker-compose.yml.""",
    ),
]

for i, (instruccion, nombre, explicacion) in enumerate(instrucciones, 1):
    print(f"[{i}] {nombre}")
    print(f"    {instruccion}")
    print()
    for linea in explicacion.strip().split("\n"):
        print(f"    {linea}")
    print()

print("=== Regla de oro del cache ===")
print("""
  MALO (deps invalidas cuando cambia el codigo):
    COPY . .                    <- todo junto
    RUN uv sync --frozen

  BUENO (deps cacheadas aunque cambie el codigo):
    COPY pyproject.toml uv.lock ./   <- deps primero
    RUN uv sync --frozen
    COPY curso/src ./src              <- codigo despues

  Poner lo que cambia MENOS primero -> builds rapidos.
""")
