"""Docker — el problema que resuelve y como lo resuelve.

Demuestra mediante texto y analogias:
- El problema de "en mi maquina funciona"
- Que es un contenedor y como difiere de una VM
- La analogia imagen/contenedor con receta/plato
- Los comandos esenciales

No ejecuta Docker — es solo explicativo.
Los ejemplos de comandos son para ejecutar en terminal.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_13/conceptos/01_docker_conceptos.py

    # Linux
    uv run scripts/clase_13/conceptos/01_docker_conceptos.py
"""


print("=== El problema sin Docker ===")
print("""
  Desarrollador A (Windows 11):
    Python 3.11.4
    httpx versión 0.26.0
    Variable de entorno OPENWEATHER_API_KEY=abc123
    uv versión 0.4.0

  Desarrollador B (Ubuntu 22.04 en VM):
    Python 3.12.1
    httpx versión 0.27.2 (breaking change en parsing de headers)
    Variable de entorno OPENWEATHER_API_KEY no definida
    uv versión 0.5.0

  Resultado:
    A: "Me funciona perfecto."
    B: "A mi me da error en la linea 47."
    A: "En mi maquina funciona..."
""")

print("=== La solucion: contenedores Docker ===")
print("""
  Un contenedor empaqueta TODO lo necesario para correr la app:
    - Sistema operativo minimo (Linux slim)
    - Version exacta de Python
    - Dependencias exactas (segun uv.lock)
    - Variables de entorno configuradas
    - El codigo fuente

  Resultado:
    El mismo contenedor corre IDENTICO en:
      - Tu portatil (Windows, Mac, Linux)
      - La VM del alumno (Ubuntu 24.04)
      - Un servidor en la nube (AWS, Azure, GCP)
      - La maquina de CI de GitHub

  "En mi maquina funciona" -> "En cualquier maquina funciona"
""")

print("=== Diferencia: VM vs Contenedor ===")
print("""
  Maquina Virtual (VM):
    Host OS
    └── Hypervisor (VMware, VirtualBox, KVM)
        └── Guest OS completo (Linux 2GB+)
            └── Tu app

  Contenedor:
    Host OS
    └── Docker Engine (comparte el kernel del host)
        └── Tu app (solo el proceso + sus deps)

  VM:         pesada, lenta de arrancar, aislamiento total
  Contenedor: ligera (~100MB), arranca en segundos, aislamiento suficiente
""")

print("=== La analogia: imagen vs contenedor ===")
print("""
  Imagen Docker  ←→  Receta de cocina
  Contenedor     ←→  El plato preparado

  La misma receta produce el mismo plato en cualquier cocina del mundo.
  Puedes preparar 10 platos (contenedores) de la misma receta (imagen).
  La receta no cambia cuando preparas el plato.
""")

print("=== Comandos esenciales ===")
comandos = [
    ("docker build -t pycommute .", "Construir imagen desde Dockerfile (. = directorio actual)"),
    ("docker run -p 8000:8000 pycommute", "Correr la imagen como contenedor, exponer puerto 8000"),
    ("docker ps", "Ver contenedores corriendo"),
    ("docker logs <id>", "Ver logs de un contenedor"),
    ("docker stop <id>", "Detener un contenedor"),
    ("docker compose up --build", "Construir y correr todos los servicios del compose"),
    ("docker compose up", "Correr servicios (sin rebuild — mas rapido si no cambia el codigo)"),
    ("docker compose down", "Detener y eliminar contenedores (los volumenes persisten)"),
    ("docker compose logs api", "Ver logs del servicio 'api' en tiempo real"),
    ("docker compose down -v", "Detener, eliminar contenedores Y volumenes (borra modelos Ollama)"),
]
for cmd, desc in comandos:
    print(f"  $ {cmd}")
    print(f"    -> {desc}\n")
