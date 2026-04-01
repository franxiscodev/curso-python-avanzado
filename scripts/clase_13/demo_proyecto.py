"""Demo Clase 13 — Demo final del curso: el sistema completo en Docker.

Muestra el estado final del proyecto con instrucciones para:
1. Arrancar el sistema con Docker Compose
2. Verificar que todos los componentes estan corriendo
3. Hacer una consulta real a la API en Docker
4. Ver los logs del contenedor

Este script NO arranca Docker automaticamente — muestra las instrucciones
paso a paso y verifica si el servidor ya esta corriendo.

Si quieres el demo automatico (arrancar servidor + consultar + parar),
ver scripts/clase_12/demo_proyecto.py — usa el mismo patron con httpx.

Ejecutar:
    # Windows (PowerShell) — desde la raiz del repo
    uv run python curso/scripts/clase_13/demo_proyecto.py

    # Linux — desde la raiz del repo
    uv run python curso/scripts/clase_13/demo_proyecto.py
"""

import sys

import anyio
import httpx
from loguru import logger

API_URL = "http://localhost:8000"


async def verificar_api() -> bool:
    """Comprueba si la API esta corriendo en localhost:8000."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{API_URL}/health")
            return response.status_code == 200
    except (httpx.ConnectError, httpx.ReadError, httpx.TimeoutException):
        return False


async def demo_api_en_docker() -> None:
    """Consulta la API si esta corriendo, muestra instrucciones si no."""
    logger.info("=== PyCommute Elite — Demo Final del Curso ===")
    logger.info("Verificando si la API esta corriendo en {url}...", url=API_URL)

    api_corriendo = await verificar_api()

    if not api_corriendo:
        logger.warning("La API no esta corriendo en {url}", url=API_URL)
        logger.info("")
        logger.info("Para arrancar el sistema completo con Docker Compose:")
        logger.info("")
        logger.info("  # Desde curso/ (donde esta el docker-compose.yml):")
        logger.info("")
        logger.info("  # Windows (PowerShell)")
        logger.info("  cd curso")
        logger.info("  docker compose up --build")
        logger.info("")
        logger.info("  # Linux")
        logger.info("  cd curso")
        logger.info("  docker compose up --build")
        logger.info("")
        logger.info("Cuando veas 'Application startup complete.' en los logs,")
        logger.info("vuelve a ejecutar este script en otro terminal.")
        logger.info("")
        logger.info("NOTA: la primera vez tarda mas — descarga las imagenes de Docker Hub.")
        logger.info("      Las veces siguientes es mucho mas rapido (cache de layers).")
        return

    logger.info("API corriendo. Consultando endpoints...")

    async with httpx.AsyncClient(base_url=API_URL, timeout=30.0) as client:
        # ── GET /health ───────────────────────────────────────────────────
        logger.info("=== GET /health ===")
        response = await client.get("/health")
        data = response.json()
        logger.info(
            "Status: {status} | Version: {version}",
            status=data["status"],
            version=data["version"],
        )
        for adapter, nombre in data["adapters"].items():
            logger.info("  {adapter}: {nombre}", adapter=adapter, nombre=nombre)

        # ── GET /cities ───────────────────────────────────────────────────
        logger.info("=== GET /cities ===")
        response = await client.get("/cities")
        cities_data = response.json()
        logger.info(
            "{total} ciudades disponibles: {muestra}...",
            total=cities_data["total"],
            muestra=", ".join(cities_data["cities"][:5]),
        )

        # ── POST /commute/ ────────────────────────────────────────────────
        logger.info("=== POST /commute/ (include_ai=false para demo rapido) ===")
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

        # ── GET /commute/history ──────────────────────────────────────────
        logger.info("=== GET /commute/history ===")
        response = await client.get("/commute/history")
        history = response.json()
        logger.info("{n} entradas en el historial", n=len(history))

    logger.info("")
    logger.info("=== Sistema corriendo en Docker ===")
    logger.info("Swagger UI: http://localhost:8000/docs")
    logger.info("Parar: docker compose down  (desde curso/)")


async def main() -> None:
    """Punto de entrada del demo."""
    logger.info("=== Demo Final — Clase 13: Docker Compose + GitHub Actions ===")
    logger.info("")
    logger.info("Este script verifica si la API esta corriendo en Docker.")
    logger.info("Si no esta corriendo, muestra como arrancarla.")
    logger.info("")

    await demo_api_en_docker()

    logger.info("")
    logger.info("=== Lo que construimos en 13 clases ===")
    hitos = [
        ("Clase 01", "Primera llamada real a OpenWeather API"),
        ("Clase 02", "Pattern Matching sobre JSONs de dos APIs"),
        ("Clase 03", "Loguru + Pydantic-Settings + @retry"),
        ("Clase 04", "57 tests que no consumen cuota de API"),
        ("Clase 05", "async/await + anyio + orquestador de rutas"),
        ("Clase 06", "lru_cache + generadores + profiling"),
        ("Clase 07", "heapq para ranking + deque para historial"),
        ("Clase 08", "Arquitectura Hexagonal con Protocol"),
        ("Clase 09", "Pydantic V2 — contratos entre capas"),
        ("Clase 10", "Gemini API con respuestas estructuradas"),
        ("Clase 11", "Ollama local + FallbackAIAdapter"),
        ("Clase 12", "FastAPI con 5 endpoints + /docs automatico"),
        ("Clase 13", "Docker Compose + GitHub Actions CI"),
    ]
    for clase, hito in hitos:
        logger.info("  {clase}: {hito}", clase=clase, hito=hito)

    logger.info("")
    logger.info("Cada clase agrego una capa. Ninguna rompio lo anterior.")
    logger.info("Eso es arquitectura de software profesional.")


anyio.run(main)
