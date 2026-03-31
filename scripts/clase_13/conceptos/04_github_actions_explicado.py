"""GitHub Actions — cada seccion del workflow explicada.

Muestra el ci.yml de PyCommute paso a paso con comentarios detallados
sobre triggers, jobs, steps, uses vs run, y variables de entorno en CI.

Enfasis en:
- Por que los tests pasan con keys falsas (diseno con mocks desde Clase 4)
- Diferencia entre uses (accion predefinida) y run (comando shell)
- El flujo completo: push -> VM de GitHub -> resultado verde/rojo

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_13/conceptos/04_github_actions_explicado.py

    # Linux
    uv run scripts/clase_13/conceptos/04_github_actions_explicado.py
"""

print("=== GitHub Actions — que es CI/CD ===")
print("""
  CI = Continuous Integration (Integracion Continua)
  CD = Continuous Delivery/Deployment (Entrega/Despliegue Continuo)

  CI: cada vez que alguien hace push, se ejecutan automaticamente
      lint y tests para verificar que el codigo sigue funcionando.

  CD: si el CI pasa, desplegar automaticamente a produccion.
      (No lo implementamos en este curso — pero el CI es el primer paso.)

  Sin CI:
    Developer A hace push -> rompe algo sin saberlo
    Developer B hace pull -> su entorno deja de funcionar
    30 minutos perdidos buscando que cambio

  Con CI:
    Developer A hace push -> GitHub Actions corre los tests en 2 min
    Tests fallan -> check rojo en el commit -> A lo arregla antes de que nadie haga pull
    Tests pasan -> check verde -> todo bien
""")

print("=== El archivo ci.yml — estructura ===")
print("""
  Ubicacion: .github/workflows/ci.yml
  (El directorio .github esta en la RAIZ del repo, no en curso/)

  Estructura basica:
    name: ...         <- nombre del workflow (aparece en GitHub)
    on: ...           <- cuando se ejecuta (triggers)
    jobs:             <- que hace
      <nombre-job>:
        runs-on: ...  <- en que maquina virtual
        steps:        <- pasos del job
          - name: ... <- nombre del step (aparece en GitHub)
            uses: ... <- usar una accion predefinida
            run: ...  <- ejecutar un comando shell
""")

print("=== Triggers — cuando se ejecuta ===")
triggers = [
    (
        "push: branches: [main]",
        "En cada push a main",
        "Verifica que el codigo pusheado no rompe nada",
    ),
    (
        "pull_request: branches: [main]",
        "En cada PR hacia main",
        "Verifica antes de mergear — si falla, bloquea el merge",
    ),
]
for trigger, cuando, para_que in triggers:
    print(f"  {trigger}")
    print(f"    Cuando: {cuando}")
    print(f"    Para que: {para_que}\n")

print("=== uses: vs run: ===")
print("""
  uses: actions/checkout@v4
    -> Usa una 'Action' predefinida de GitHub Marketplace.
    -> 'actions/checkout' es codigo Python/JS que descarga el repo.
    -> @v4 es la version. Siempre pinear a una version para reproducibilidad.
    -> Ventaja: no hay que escribir el comando de git clone manualmente.

  run: uv run pytest tests/ -v
    -> Ejecuta un comando shell normal.
    -> El mismo comando que usas en tu maquina.
    -> Si el comando sale con codigo != 0, el step falla.
""")

print("=== Los steps de PyCommute — explicados ===")
steps = [
    (
        "actions/checkout@v4",
        "Descarga el codigo del repo en la VM de GitHub",
        "Sin este step la VM no tiene acceso al repositorio",
    ),
    (
        "astral-sh/setup-uv@v3",
        "Instala UV en la VM",
        "Igual que tener UV instalado en tu maquina — agrega 'uv' al PATH",
    ),
    (
        "uv python install 3.12",
        "Instala Python 3.12 con UV",
        "UV gestiona versiones de Python ademas de dependencias",
    ),
    (
        "uv sync --all-extras",
        "Instala todas las dependencias",
        "--all-extras incluye pytest, ruff y otras deps de desarrollo",
    ),
    (
        "uv run ruff check src/",
        "Verifica el estilo del codigo",
        "Si hay errores de lint -> step falla -> job falla -> check rojo",
    ),
    (
        "uv run pytest tests/ -v --tb=short",
        "Corre todos los tests",
        "Si algun test falla -> step falla -> job falla -> check rojo",
    ),
]
for cmd, que_hace, por_que in steps:
    print(f"  {cmd}")
    print(f"    Que hace: {que_hace}")
    print(f"    Por que: {por_que}\n")

print("=== Por que los tests pasan con keys falsas ===")
print("""
  En el workflow, las variables de entorno son strings como 'test-key':
    env:
      OPENWEATHER_API_KEY: 'test-key'
      GOOGLE_API_KEY: 'test-key'

  Esto funciona porque los tests MOCKEAN los adaptadores externos.
  Los mocks no hacen llamadas reales a las APIs.
  Solo necesitan que pydantic-settings vea ALGUNA cadena — no una key valida.

  El diseno con mocks de Clase 4 pagó en Clase 13:
    - CI no necesita secrets reales en GitHub
    - Tests corren sin internet
    - Tests corren en segundos, no en segundos x cuota de API

  Si un test fallara porque necesita la API real:
    - Seria un test de integracion, no unitario
    - Habria que configurar GitHub Secrets
    - El CI dependeria de la disponibilidad de servicios externos
""")

print("=== Flujo completo ===")
print("""
  git push origin main
      |
      v
  GitHub detecta el push
      |
      v
  Crea una VM Ubuntu 24.04 limpia
      |
      v
  Ejecuta los steps en orden:
    1. Descarga el codigo
    2. Instala UV
    3. Instala Python 3.12
    4. Instala dependencias
    5. Lint con ruff -> OK o FALLO
    6. Tests con pytest -> OK o FALLO
      |
      v
  Resultado:
    Todos los steps OK -> check verde en el commit en GitHub
    Algun step falla  -> check rojo + notificacion por email
""")
