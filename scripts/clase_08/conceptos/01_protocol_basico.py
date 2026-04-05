"""
Concepto 1: typing.Protocol y duck typing estructural.

Protocol permite definir contratos de comportamiento sin forzar herencia.
Cualquier clase que tenga los métodos con la firma correcta satisface
el Protocol automáticamente — esto es duck typing estructural.

RoutePort declara get_eta_minutes como async: los adaptadores que lo
implementen también deben usar async def o los type checkers lo rechazan.

@runtime_checkable habilita isinstance() en tiempo de ejecución.
Sin él, isinstance(obj, RoutePort) lanzaría TypeError.
La verificación solo comprueba que los métodos existen, no sus firmas —
para la verificación completa de tipos hay que usar mypy/pyright.

OpenRouteAdapter y GoogleMapsAdapter NO heredan de RoutePort.
El isinstance check prueba que Python los reconoce como conformes
solo por su estructura (duck typing).

Conexión con el proyecto:
  core/ports.py contiene WeatherPort, RoutePort, CachePort — el mismo
  patrón. OpenWeatherAdapter y OpenRouteAdapter los implementan sin herencia.

Ejecutar:
  uv run python scripts/clase_08/conceptos/01_protocol_basico.py
"""

import asyncio
from typing import Protocol, runtime_checkable


# 1. El Puerto (Lo que el Core exige)
@runtime_checkable
class RoutePort(Protocol):
    async def get_eta_minutes(self, origin: str, destination: str) -> int:
        """Devuelve el tiempo estimado de llegada en minutos."""
        ...


# 2. Los Adaptadores (Las implementaciones concretas)
class OpenRouteAdapter:
    async def get_eta_minutes(self, origin: str, destination: str) -> int:
        print(f"[OpenRoute] Calculando ruta de {origin} a {destination}...")
        await asyncio.sleep(0.1)  # Simulando I/O
        return 45


class GoogleMapsAdapter:
    async def get_eta_minutes(self, origin: str, destination: str) -> int:
        print(f"[GoogleMaps] Calculando ruta de {origin} a {destination}...")
        await asyncio.sleep(0.1)
        return 42


async def main():
    # Validación estructural (Duck Typing)
    ors_adapter = OpenRouteAdapter()

    # Mypy y el linter estarán felices si RoutePort es el tipo esperado
    if isinstance(ors_adapter, RoutePort):
        eta = await ors_adapter.get_eta_minutes("Madrid", "Valencia")
        print(f"ETA: {eta} mins")


if __name__ == "__main__":
    asyncio.run(main())
