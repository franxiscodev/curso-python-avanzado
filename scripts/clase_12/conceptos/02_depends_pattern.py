"""Patron Depends() — inyeccion de dependencias en FastAPI.

Demuestra:
- La diferencia entre sin cache y con lru_cache
- Por que lru_cache convierte get_*() en un singleton
- Como dependency_overrides permite reemplazar dependencias en tests

No ejecuta FastAPI — todo simulado con Python puro.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_12/conceptos/02_depends_pattern.py

    # Linux
    uv run scripts/clase_12/conceptos/02_depends_pattern.py
"""

from functools import lru_cache


# ── Simulacion de una dependencia "pesada" ────────────────────────────
class ServicioExterno:
    """Simula un servicio caro de crear (DB connection, API client, etc.)."""

    _contador = 0

    def __init__(self, nombre: str) -> None:
        ServicioExterno._contador += 1
        self.nombre = nombre
        self.instancia_num = ServicioExterno._contador
        print(f"  [{self.instancia_num}] Creando {nombre} (costo: inicializacion)")

    def procesar(self, dato: str) -> str:
        return f"{self.nombre}[{self.instancia_num}] procesó: {dato}"


# ── Sin cache — se crea en cada "request" ────────────────────────────
def get_servicio_sin_cache() -> ServicioExterno:
    return ServicioExterno("ServicioSinCache")


# ── Con lru_cache — se crea solo una vez ─────────────────────────────
@lru_cache
def get_servicio_con_cache() -> ServicioExterno:
    return ServicioExterno("ServicioConCache")


print("=== Sin lru_cache: 3 'requests' = 3 instancias ===")
for i in range(1, 4):
    servicio = get_servicio_sin_cache()
    resultado = servicio.procesar(f"request {i}")
    print(f"  Request {i}: id={id(servicio)} -> {resultado}")

print("\n=== Con lru_cache: 3 'requests' = 1 instancia ===")
for i in range(1, 4):
    servicio = get_servicio_con_cache()
    resultado = servicio.procesar(f"request {i}")
    print(f"  Request {i}: id={id(servicio)} -> {resultado}")

print("\n=== En FastAPI con Depends() ===")
print("""
  # Sin cache — nueva instancia por request:
  @router.get("/items")
  async def items(svc = Depends(get_servicio_sin_cache)):
      return svc.procesar("datos")

  # Con cache — singleton compartido entre todos los requests:
  @router.get("/items")
  async def items(svc = Depends(get_servicio_con_cache)):
      return svc.procesar("datos")
""")

print("=== dependency_overrides en tests ===")
print("""
  # En tests, reemplazar la dependencia real por un mock:
  def mock_servicio():
      svc = MagicMock()
      svc.procesar.return_value = "respuesta simulada"
      return svc

  app.dependency_overrides[get_servicio_con_cache] = mock_servicio
  # Ahora todos los endpoints que usen Depends(get_servicio_con_cache)
  # reciben el mock — sin patchear modulos, sin imports complicados.
""")
