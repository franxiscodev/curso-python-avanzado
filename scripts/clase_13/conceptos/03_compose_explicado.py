"""Docker Compose — cada seccion explicada con su proposito.

Muestra el docker-compose.yml de PyCommute sección por seccion con
comentarios detallados sobre el networking interno, volumenes y variables
de entorno.

Enfasis en:
- Por que los servicios se comunican por nombre (http://ollama:11434)
- Diferencia entre volumenes nombrados y bind mounts
- Como Docker Compose lee el .env del host

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_13/conceptos/03_compose_explicado.py

    # Linux
    uv run scripts/clase_13/conceptos/03_compose_explicado.py
"""

print("=== Docker Compose — para que sirve ===")
print("""
  Un Dockerfile define COMO construir UNA imagen.
  Docker Compose define COMO correr MULTIPLES servicios juntos.

  PyCommute necesita dos servicios corriendo al mismo tiempo:
    api    -> la API FastAPI (nuestro codigo)
    ollama -> el servidor de IA local (imagen publica de Docker Hub)

  Sin Compose: dos comandos docker run manuales, red manual, configuracion manual.
  Con Compose: un solo archivo YAML + docker compose up.
""")

print("=== Seccion: services ===")
print("""
  services:
    <nombre>:          <- nombre del servicio (tambien es su hostname en la red)
      build: .         <- construir desde Dockerfile (para codigo propio)
      image: ...       <- usar imagen de Docker Hub (para servicios externos)
      ports: [...]     <- mapear puertos host:contenedor
      environment: ... <- variables de entorno
      depends_on: ...  <- orden de arranque
      volumes: [...]   <- persistir datos
      restart: ...     <- politica de reinicio
""")

print("=== El concepto mas importante: networking interno ===")
print("""
  Docker Compose crea una red privada para todos los servicios.
  Dentro de esa red, cada servicio es accesible POR SU NOMBRE.

  En nuestro docker-compose.yml:
    - El servicio se llama "ollama"
    - Dentro de la red, su hostname es "ollama"
    - La API puede conectarse a el en: http://ollama:11434

  Comparacion:
    Sin Docker:  OLLAMA_BASE_URL=http://localhost:11434  (proceso local)
    Con Compose: OLLAMA_BASE_URL=http://ollama:11434     (servicio por nombre)

  Por eso en docker-compose.yml tenemos:
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      #                          ^^^^^^
      #                          nombre del servicio = hostname en la red
""")

print("=== Variables de entorno — tres formas ===")
variables = [
    (
        "- OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}",
        "Leer del .env del host",
        "Docker Compose busca .env en el mismo directorio que compose.yml",
    ),
    (
        "- OLLAMA_BASE_URL=http://ollama:11434",
        "Valor fijo",
        "Siempre igual — no depende del host ni del entorno",
    ),
    (
        "- OLLAMA_MODEL=${OLLAMA_MODEL:-gemma3:1b}",
        "Con valor por defecto",
        "${VAR:-default}: si VAR no esta en .env, usa 'default'",
    ),
]
for var, tipo, explicacion in variables:
    print(f"  {var}")
    print(f"    Tipo: {tipo}")
    print(f"    Uso: {explicacion}\n")

print("=== Volumenes — persistir datos entre reinicios ===")
print("""
  Sin volumen:
    docker compose down  ->  todos los modelos de Ollama se pierden
    docker compose up    ->  vuelve a descargar gemma3:1b (~800MB)

  Con volumen nombrado:
    volumes:
      - ollama_data:/root/.ollama  <- host_volume:ruta_en_contenedor

    docker compose down  ->  el volumen ollama_data persiste en el host
    docker compose up    ->  Ollama encuentra los modelos, arranca rapido

  docker compose down    ->  elimina contenedores, PRESERVA volumenes
  docker compose down -v ->  elimina contenedores Y volumenes (reset total)
""")

print("=== depends_on — orden de arranque ===")
print("""
  api:
    depends_on:
      - ollama   <- Docker arranca ollama antes que api

  IMPORTANTE: depends_on espera a que el CONTENEDOR arranque,
  no a que el SERVICIO este listo para responder.
  Ollama puede tardar unos segundos en cargar el modelo.
  En produccion se usaria healthcheck para esperar a que Ollama responda.
""")

print("=== Comandos de uso ===")
comandos = [
    ("docker compose up --build", "Construir imagen y arrancar todos los servicios"),
    ("docker compose up", "Arrancar sin rebuild (mas rapido si el codigo no cambio)"),
    ("docker compose up -d", "Arrancar en segundo plano (detached)"),
    ("docker compose down", "Detener y eliminar contenedores"),
    ("docker compose logs api", "Ver logs del servicio api"),
    ("docker compose logs -f api", "Ver logs en tiempo real (follow)"),
    ("docker compose ps", "Ver estado de los servicios"),
    ("docker compose exec api bash", "Abrir shell dentro del contenedor api"),
]
for cmd, desc in comandos:
    print(f"  $ {cmd}")
    print(f"    -> {desc}\n")
