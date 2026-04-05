"""
Concepto 1: Ciclo de vida y estado global en FastAPI.

FastAPI expone un hook 'lifespan' que separa claramente startup de shutdown:
- STARTUP: se ejecuta antes de que la app acepte peticiones — ideal para
  inicializar recursos costosos (httpx.AsyncClient, pools de DB, modelos ML).
- SHUTDOWN: se ejecuta al apagar (Ctrl+C o señal SIGTERM) — garantiza
  que las conexiones se cierran aunque haya una excepción.

app.state es el almacén de estado compartido entre peticiones:
- Se asigna en startup: app.state.http_client = httpx.AsyncClient()
- Se accede en endpoints via request.app.state.http_client
- Un solo cliente HTTP para toda la app — sin crear/destruir por petición.

Ejecutar:
  uv run uvicorn scripts.clase_12.conceptos.01_fastapi_lifespan:app --reload
  curl http://localhost:8000/health
"""

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # [STARTUP] Aquí inicializamos recursos costosos (ej. httpx.AsyncClient o Pools de DB)
    logger.info("🚀 Inicializando recursos globales...")
    app.state.http_client = httpx.AsyncClient()
    yield  # Aquí la aplicación está sirviendo peticiones
    # [SHUTDOWN] Limpieza garantizada al apagar (Ctrl+C)
    logger.info("🛑 Cerrando conexiones y liberando memoria...")
    await app.state.http_client.aclose()


app = FastAPI(title="PyCommute API Pro", lifespan=lifespan)


@app.get("/health")
async def health_check(request: Request):
    # Accedemos al cliente global de forma segura
    client = request.app.state.http_client
    return {"status": "ok", "client_active": not client.is_closed}
