"""
Concepto 2: Inyección de dependencias con FastAPI Depends.

FastAPI resuelve dependencias automáticamente antes de llamar al endpoint:
- get_commute_service() es la fábrica — crea el servicio con sus propias deps.
- Depends(get_commute_service) le dice a FastAPI que llame a esa fábrica.
- Annotated[CommuteService, Depends(...)] es la forma moderna (PEP 593):
  un alias de tipo que incluye el metadato de inyección.

Beneficios sobre instanciar en el endpoint:
- Testeable: dependency_overrides en tests sin tocar el endpoint.
- Reutilizable: la misma dep en múltiples endpoints.
- Ciclo de vida controlado: la fábrica puede usar yield para cleanup.

El endpoint solo orquesta — no crea, no calcula, no importa la clase.

Ejecutar:
  uv run uvicorn scripts.clase_12.conceptos.02_depends_pattern:app --reload
  curl "http://localhost:8000/api/v1/eta?origin=Valencia&destination=Madrid"
"""

from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI()


# 1. Simulación de nuestro Dominio (Capa Interna)
class CommuteService:
    def calculate_eta(self, origin: str, dest: str) -> int:
        return 42  # Lógica compleja aislada aquí


# 2. El proveedor de la dependencia (Fábrica)
def get_commute_service() -> CommuteService:
    # Aquí podríamos inyectar la DB o la API Key al servicio
    return CommuteService()


# 3. Contrato de Tipo para FastAPI
ServiceDep = Annotated[CommuteService, Depends(get_commute_service)]


# 4. El Endpoint (Capa HTTP)
@app.get("/api/v1/eta")
def get_eta(origin: str, destination: str, service: ServiceDep):
    # El endpoint solo orquesta, no calcula nada.
    eta = service.calculate_eta(origin, destination)
    return {"origin": origin, "destination": destination, "eta_minutes": eta}
