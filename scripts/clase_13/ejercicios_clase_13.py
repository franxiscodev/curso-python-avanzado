"""
Ejercicios — Clase 13: Deploy y CI/CD
======================================
Dos ejercicios sobre análisis de configuraciones de Docker Compose
y GitHub Actions sin necesidad de ejecutar Docker ni GitHub.

Ejecutar (desde curso/):
    uv run python scripts/clase_13/ejercicios_clase_13.py

Requisito: autocontenido, solo usa stdlib.
"""

from typing import Any


# ---------------------------------------------------------------------------
# Datos de ejemplo ya implementados — no modificar
# ---------------------------------------------------------------------------

COMPOSE_EJEMPLO: dict[str, Any] = {
    "version": "3.8",
    "services": {
        "api": {
            "build": ".",
            "ports": ["8000:8000"],
            "environment": ["ENV=production"],
        },
        "redis": {
            "image": "redis:7-alpine",
            "ports": ["6379:6379"],
        },
        "worker": {
            "build": ".",
            "command": "python -m worker",
        },
    },
    "volumes": {
        "redis_data": None,
    },
}

WORKFLOW_EJEMPLO: dict[str, Any] = {
    "name": "CI Pipeline",
    "on": ["push", "pull_request"],
    "jobs": {
        "lint": {
            "runs-on": "ubuntu-latest",
            "steps": [{"uses": "actions/checkout@v4"}, {"run": "ruff check src/"}],
        },
        "test": {
            "runs-on": "ubuntu-latest",
            "steps": [{"uses": "actions/checkout@v4"}, {"run": "pytest tests/"}],
        },
        "deploy": {
            "runs-on": "ubuntu-latest",
            "needs": ["lint", "test"],
            "steps": [{"run": "docker build ."}],
        },
    },
}

WORKFLOW_INCOMPLETO: dict[str, Any] = {
    "name": "CI Incompleto",
    "on": ["push"],
    "jobs": {
        "lint": {"runs-on": "ubuntu-latest", "steps": []},
        # Falta "test" y "deploy"
    },
}


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Extraer nombres de servicios de un dict de Docker Compose
# Implementa `listar_servicios(compose_dict: dict) -> list[str]`
# Debe:
#   - Acceder a compose_dict["services"]
#   - Retornar la lista de nombres de servicios (las keys de ese dict)
#   - Si "services" no existe, retornar lista vacía []
# Ejemplo con COMPOSE_EJEMPLO → ["api", "redis", "worker"]
# Pista: repasa "Estructura de docker-compose.yml" en 01_conceptos.md
def listar_servicios(compose_dict: dict) -> list[str]:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — Validar que un workflow tiene los jobs requeridos
# Implementa `validar_workflow(workflow_dict: dict, jobs_requeridos: list[str]) -> bool`
# Debe:
#   - Acceder a workflow_dict["jobs"]
#   - Verificar que todos los strings de jobs_requeridos son keys de ese dict
#   - Retornar True si todos existen, False si falta alguno
#   - Si "jobs" no existe en workflow_dict, retornar False
# Ejemplo con WORKFLOW_EJEMPLO y ["lint", "test", "deploy"] → True
# Ejemplo con WORKFLOW_INCOMPLETO y ["lint", "test", "deploy"] → False
# Pista: repasa "Estructura de GitHub Actions" en 01_conceptos.md
def validar_workflow(workflow_dict: dict, jobs_requeridos: list[str]) -> bool:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo — muestra los resultados (no modificar)
# ---------------------------------------------------------------------------

def demo() -> None:
    print("=== Ejercicio 1: listar_servicios ===")
    servicios = listar_servicios(COMPOSE_EJEMPLO)
    if servicios is not None:
        print(f"  Servicios encontrados: {servicios}")
        print(f"  Total: {len(servicios)} servicio(s)")
    else:
        print("  Sin implementar aún.")

    compose_sin_servicios: dict = {"version": "3.8"}
    servicios_vacios = listar_servicios(compose_sin_servicios)
    if servicios_vacios is not None:
        print(f"  Sin clave 'services' → {servicios_vacios}")
    else:
        print("  Sin implementar aún.")

    print("\n=== Ejercicio 2: validar_workflow ===")
    jobs_completos = ["lint", "test", "deploy"]
    jobs_parciales = ["lint", "test", "deploy"]

    resultado_completo = validar_workflow(WORKFLOW_EJEMPLO, jobs_completos)
    if resultado_completo is not None:
        print(f"  Workflow completo con {jobs_completos} → {resultado_completo}")
    else:
        print("  Sin implementar aún.")

    resultado_incompleto = validar_workflow(WORKFLOW_INCOMPLETO, jobs_parciales)
    if resultado_incompleto is not None:
        print(f"  Workflow incompleto con {jobs_parciales} → {resultado_incompleto}")
    else:
        print("  Sin implementar aún.")

    resultado_sin_jobs = validar_workflow({"name": "vacío"}, ["lint"])
    if resultado_sin_jobs is not None:
        print(f"  Sin clave 'jobs' → {resultado_sin_jobs}")
    else:
        print("  Sin implementar aún.")


if __name__ == "__main__":
    demo()
