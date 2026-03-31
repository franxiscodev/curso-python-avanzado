"""Aplicacion FastAPI de PyCommute.

# [CLASE 12] Nueva capa api/ — expone CommuteService como API REST.
# La arquitectura hexagonal hace que agregar FastAPI no requiera
# cambiar ninguno de los modulos existentes (core/, adapters/, services/).
# FastAPI es un adaptador mas — recibe HTTP y delega al servicio.
# Antes (Clase 11): CommuteService solo usable desde scripts Python.
# [CLASE 13 ->] Esta app se empaqueta en Docker Compose junto con Gradio.
#               uvicorn corre como servicio, Gradio como frontend.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from pycommute import __version__
from pycommute.api.routers import cities, commute, health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup y shutdown del servidor."""
    logger.info("PyCommute API v{version} iniciando...", version=__version__)
    yield
    logger.info("PyCommute API cerrando...")


app = FastAPI(
    title="PyCommute API",
    description="Asesor de movilidad inteligente con IA hibrida (Gemini + Ollama fallback)",
    version=__version__,
    lifespan=lifespan,
)

app.include_router(health.router, tags=["health"])
app.include_router(cities.router, tags=["cities"])
app.include_router(commute.router, tags=["commute"])
