"""Router del endpoint GET /cities."""

from fastapi import APIRouter

from pycommute.adapters.cache import _COORDENADAS
from pycommute.api.schemas import CitiesResponse

router = APIRouter()


@router.get("/cities", response_model=CitiesResponse)
async def get_cities() -> CitiesResponse:
    """Lista de ciudades disponibles para consultar."""
    cities = sorted(_COORDENADAS.keys())
    return CitiesResponse(cities=cities, total=len(cities))
