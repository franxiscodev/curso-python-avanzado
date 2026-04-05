"""
Concepto 3: Schemas Pydantic como contratos de entrada y salida.

FastAPI usa Pydantic V2 para validar automáticamente el cuerpo de las peticiones:
- RoutingRequest valida la entrada: Field(...) requiere el campo, min_length
  garantiza longitud mínima, pattern restringe los valores permitidos.
- model_validator(mode="after") ejecuta validación cruzada entre campos:
  origen y destino no pueden ser iguales — imposible de expresar con Field solo.
- RoutingResponse filtra la salida: solo los campos declarados se serializan,
  datos internos no se exponen accidentalmente.

Si el payload no cumple el contrato, FastAPI devuelve 422 automáticamente
con detalle de qué campo falló — sin código adicional.

response_model=RoutingResponse en el decorador activa el filtrado de salida.

Ejecutar:
  uv run uvicorn scripts.clase_12.conceptos.03_pydantic_schemas:app --reload
  curl -X POST http://localhost:8000/route -H "Content-Type: application/json" \
       -d '{"origin": "Valencia", "destination": "Madrid"}'
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator

app = FastAPI()


class RoutingRequest(BaseModel):
    # Validaciones a nivel de campo (Field)
    origin: str = Field(..., min_length=3, description="Ciudad de origen")
    destination: str = Field(..., min_length=3, description="Ciudad destino")
    transport_mode: str = Field(
        default="driving", pattern="^(driving|transit|walking)$"
    )

    # Validación cruzada a nivel de modelo
    @model_validator(mode="after")
    def check_different_locations(self) -> "RoutingRequest":
        if self.origin.lower() == self.destination.lower():
            raise ValueError("El origen y destino no pueden ser iguales.")
        return self


class RoutingResponse(BaseModel):
    route_id: str
    eta_mins: int
    # Excluimos datos internos accidentalmente expuestos


@app.post("/route", response_model=RoutingResponse)
def create_route(payload: RoutingRequest):
    # Si el flujo llega aquí, el payload está 100% garantizado y tipado.
    return RoutingResponse(route_id="R-999", eta_mins=120)
