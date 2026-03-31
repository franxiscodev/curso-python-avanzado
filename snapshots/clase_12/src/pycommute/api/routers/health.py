"""Router del endpoint GET /health."""

from fastapi import APIRouter

from pycommute import __version__
from pycommute.adapters.cache import MemoryCacheAdapter
from pycommute.adapters.route import OpenRouteAdapter
from pycommute.adapters.weather import OpenWeatherAdapter
from pycommute.api.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Estado del servicio y adaptadores configurados."""
    return HealthResponse(
        status="ok",
        version=__version__,
        adapters={
            "weather": OpenWeatherAdapter.__name__,
            "route": OpenRouteAdapter.__name__,
            "cache": MemoryCacheAdapter.__name__,
        },
    )
