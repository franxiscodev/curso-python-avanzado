"""Demo Clase 12 — API REST con FastAPI: servidor + cliente httpx.

Demuestra:
- Arrancar uvicorn en un proceso hijo
- Consultar /health, /cities y /commute/ con httpx
- Ver el historial via GET /commute/history
- Parar el servidor limpiamente

Ejecutar desde la raiz del repo:
    # Windows (PowerShell)
    uv run python curso/scripts/clase_12/demo_proyecto.py

    # Linux
    uv run python curso/scripts/clase_12/demo_proyecto.py

Requisitos:
    - .env con claves validas en curso/
    - El servidor se arranca y para automaticamente
"""

import subprocess
import sys
import time
from pathlib import Path

import anyio
import httpx
from loguru import logger

# Directorio desde el que arrancar uvicorn (necesita el .env con las claves)
CURSO_DIR = Path(__file__).parent.parent.parent
BASE_URL = "http://127.0.0.1:8001"
UVICORN_CMD = [
    sys.executable,
    "-m",
    "uvicorn",
    "pycommute.api.main:app",
    "--port",
    "8001",
    "--log-level",
    "warning",
]


async def main() -> None:
    """Arranca el servidor, hace consultas y lo para."""
    # ── Arrancar servidor ─────────────────────────────────────────────
    logger.info("Arrancando PyCommute API en {url}...", url=BASE_URL)
    server = subprocess.Popen(
        UVICORN_CMD,
        cwd=CURSO_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Esperar a que el servidor arranque
    await anyio.sleep(2.5)

    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            # ── GET /health ───────────────────────────────────────────
            logger.info("=== GET /health ===")
            response = await client.get("/health")
            data = response.json()
            logger.info(
                "Status: {status} | Version: {version}",
                status=data["status"],
                version=data["version"],
            )
            for adapter, name in data["adapters"].items():
                logger.info("  {adapter}: {name}", adapter=adapter, name=name)

            # ── GET /cities ───────────────────────────────────────────
            logger.info("=== GET /cities ===")
            response = await client.get("/cities")
            cities_data = response.json()
            logger.info(
                "{total} ciudades disponibles: {sample}...",
                total=cities_data["total"],
                sample=", ".join(cities_data["cities"][:5]),
            )

            # ── POST /commute/ ────────────────────────────────────────
            logger.info("=== POST /commute/ (sin IA para demo rapido) ===")
            response = await client.post(
                "/commute/",
                json={
                    "origin_city": "Valencia",
                    "destination_city": "Madrid",
                    "profiles": ["driving-car", "cycling-regular"],
                    "include_ai": False,
                },
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    "{origin} -> {dest}",
                    origin=result["origin_city"],
                    dest=result["destination_city"],
                )
                logger.info(
                    "Clima origen: {temp}C, {desc}",
                    temp=result["origin_weather"]["temperature"],
                    desc=result["origin_weather"]["description"],
                )
                logger.info(
                    "Clima destino: {temp}C, {desc}",
                    temp=result["destination_weather"]["temperature"],
                    desc=result["destination_weather"]["description"],
                )
                logger.info("Rutas ({n}):", n=len(result["routes"]))
                for route in result["routes"]:
                    marker = " <- mejor" if route == result.get("best_route") else ""
                    logger.info(
                        "  {profile}: {km}km, {min}min{marker}",
                        profile=route["profile"],
                        km=route["distance_km"],
                        min=route["duration_min"],
                        marker=marker,
                    )
            else:
                logger.error(
                    "Error {status}: {detail}",
                    status=response.status_code,
                    detail=response.text[:200],
                )

            # ── GET /commute/history ──────────────────────────────────
            logger.info("=== GET /commute/history ===")
            response = await client.get("/commute/history")
            history = response.json()
            logger.info("{n} entradas en el historial", n=len(history))
            for entry in history:
                logger.info(
                    "  {ts} | {city} | {profile}",
                    ts=entry["timestamp"][:19],
                    city=entry["origin_city"],
                    profile=entry["best_profile"],
                )

    finally:
        # ── Parar servidor ────────────────────────────────────────────
        logger.info("Parando servidor...")
        server.terminate()
        server.wait(timeout=5)
        logger.info("Demo completado.")


anyio.run(main)
