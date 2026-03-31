"""Concepto 04 — Arquitectura Hexagonal completa en miniatura.

Hexagonal = Puertos + Adaptadores + Nucleo puro.
Este ejemplo autocontenido simula la misma estructura de PyCommute
en ~100 lineas sin dependencias externas.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_08/conceptos/04_hexagonal_completo.py

    # Linux
    uv run scripts/clase_08/conceptos/04_hexagonal_completo.py
"""

import asyncio
from typing import Any, Protocol, runtime_checkable


# ┌─────────────────────────────────────────────────────────────────────┐
# │  PUERTOS — contratos definidos por el nucleo                        │
# └─────────────────────────────────────────────────────────────────────┘

@runtime_checkable
class ClimaPort(Protocol):
    async def obtener(self, ciudad: str) -> dict[str, Any]: ...


@runtime_checkable
class RutaPort(Protocol):
    async def calcular(self, origen: str, destino: str) -> dict[str, Any]: ...


# ┌─────────────────────────────────────────────────────────────────────┐
# │  ADAPTADORES — implementaciones concretas (simuladas)               │
# └─────────────────────────────────────────────────────────────────────┘

class ClimaFakeAdapter:
    """Adaptador fake — simula una API de clima sin HTTP."""

    _DATOS = {
        "Valencia": {"temperatura": 22.0, "descripcion": "soleado"},
        "Madrid":   {"temperatura": 28.0, "descripcion": "despejado"},
    }

    async def obtener(self, ciudad: str) -> dict[str, Any]:
        return self._DATOS.get(ciudad, {"temperatura": 20.0, "descripcion": "sin datos"})


class RutaFakeAdapter:
    """Adaptador fake — simula una API de rutas sin HTTP."""

    async def calcular(self, origen: str, destino: str) -> dict[str, Any]:
        return {
            "origen": origen,
            "destino": destino,
            "distancia_km": 350.0,
            "duracion_min": 210,
        }


# ┌─────────────────────────────────────────────────────────────────────┐
# │  SERVICIO (nucleo) — orquesta con inyeccion de dependencias         │
# └─────────────────────────────────────────────────────────────────────┘

class ViajeService:
    """Servicio de nucleo — no conoce httpx, bases de datos ni APIs."""

    def __init__(self, clima: ClimaPort, ruta: RutaPort) -> None:
        self._clima = clima
        self._ruta = ruta

    async def planificar(self, origen: str, destino: str) -> dict[str, Any]:
        """Consulta clima y ruta en paralelo, combina el resultado."""
        clima_result: dict[str, Any] = {}
        ruta_result: dict[str, Any] = {}

        async def fetch_clima() -> None:
            clima_result.update(await self._clima.obtener(origen))

        async def fetch_ruta() -> None:
            ruta_result.update(await self._ruta.calcular(origen, destino))

        await asyncio.gather(fetch_clima(), fetch_ruta())
        return {"clima": clima_result, "ruta": ruta_result}


# ┌─────────────────────────────────────────────────────────────────────┐
# │  MAIN — composicion: quien elige los adaptadores                    │
# └─────────────────────────────────────────────────────────────────────┘

async def main() -> None:
    print("=== Arquitectura Hexagonal completa ===")
    print()

    # Verificar contratos
    clima_adapter = ClimaFakeAdapter()
    ruta_adapter = RutaFakeAdapter()

    print(f"ClimaFakeAdapter satisface ClimaPort: {isinstance(clima_adapter, ClimaPort)}")
    print(f"RutaFakeAdapter satisface RutaPort:   {isinstance(ruta_adapter, RutaPort)}")
    print()

    # Construir el servicio con DI
    service = ViajeService(clima=clima_adapter, ruta=ruta_adapter)

    # Consulta completa
    resultado = await service.planificar("Valencia", "Madrid")

    clima = resultado["clima"]
    ruta = resultado["ruta"]

    print(f"Clima en Valencia: {clima['temperatura']}C, {clima['descripcion']}")
    print(f"Ruta: {ruta['distancia_km']} km, {ruta['duracion_min']} min")
    print()
    print("Capas:")
    print("  Puertos     -> ClimaPort, RutaPort        (contratos, sin implementacion)")
    print("  Adaptadores -> ClimaFakeAdapter, RutaFakeAdapter (implementan puertos)")
    print("  Servicio    -> ViajeService               (nucleo, solo logica)")
    print()
    print("ViajeService NO importa httpx, requests ni nada externo.")
    print("Para produccion: sustituir adapters por versiones reales.")


asyncio.run(main())
