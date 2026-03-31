"""Patron Fallback — resiliencia sin tocar el consumidor.

Demuestra:
- Protocol como contrato entre adaptadores
- FallbackServicio que encapsula el try/except
- El consumidor no sabe cual de los dos respondio
- Por que el fallback no va en el consumidor sino en el adaptador

No requiere Ollama ni API keys — todo simulado localmente.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_11/conceptos/03_patron_fallback.py

    # Linux
    uv run scripts/clase_11/conceptos/03_patron_fallback.py
"""

import asyncio
from typing import Protocol


# ── Puerto (contrato) ─────────────────────────────────────────────────
class ServicioPort(Protocol):
    async def procesar(self, dato: str) -> str: ...


# ── Implementaciones concretas ────────────────────────────────────────
class ServicioPrimario:
    """Servicio rapido pero poco fiable (ej: API cloud)."""

    def __init__(self, falla: bool = True) -> None:
        self._falla = falla

    async def procesar(self, dato: str) -> str:
        await asyncio.sleep(0.05)  # simula latencia de red
        if self._falla:
            raise ConnectionError("429 RESOURCE_EXHAUSTED — cuota agotada")
        return f"[Primario] {dato} procesado en la nube"


class ServicioSecundario:
    """Servicio mas lento pero siempre disponible (ej: modelo local)."""

    async def procesar(self, dato: str) -> str:
        await asyncio.sleep(0.2)  # simula latencia local
        return f"[Secundario] {dato} procesado localmente"


# ── Adaptador de fallback ─────────────────────────────────────────────
class FallbackServicio:
    """Implementa ServicioPort pero internamente usa dos adaptadores.

    El consumidor no sabe que hay un fallback — simplemente llama a procesar().
    Si el primario falla, el secundario toma el relevo automaticamente.
    """

    def __init__(self, primary: ServicioPort, secondary: ServicioPort) -> None:
        self._primary = primary
        self._secondary = secondary

    async def procesar(self, dato: str) -> str:
        primary_name = type(self._primary).__name__
        secondary_name = type(self._secondary).__name__
        try:
            print(f"  -> Intentando con {primary_name}...")
            result = await self._primary.procesar(dato)
            print(f"  -> {primary_name} respondio correctamente")
            return result
        except Exception as e:
            print(f"  -> {primary_name} fallo: {e}")
            print(f"  -> Conmutando a {secondary_name}...")
            result = await self._secondary.procesar(dato)
            print(f"  -> {secondary_name} respondio correctamente")
            return result


# ── Consumidor ────────────────────────────────────────────────────────
async def ejecutar_consulta(servicio: ServicioPort, dato: str) -> None:
    """El consumidor solo conoce ServicioPort — no sabe nada de fallbacks."""
    resultado = await servicio.procesar(dato)
    print(f"  Resultado: {resultado}")


async def main() -> None:
    print("=== Caso 1: Primario disponible (sin fallback) ===")
    servicio_ok = FallbackServicio(
        primary=ServicioPrimario(falla=False),
        secondary=ServicioSecundario(),
    )
    await ejecutar_consulta(servicio_ok, "datos de movilidad")

    print("\n=== Caso 2: Primario caido — fallback a secundario ===")
    servicio_fallback = FallbackServicio(
        primary=ServicioPrimario(falla=True),
        secondary=ServicioSecundario(),
    )
    await ejecutar_consulta(servicio_fallback, "datos de movilidad")

    print("\n=== Por que el fallback no va en el consumidor ===")
    print("""
  MAL — consumidor conoce dos implementaciones concretas:
    try:
        result = await primario.procesar(dato)
    except Exception:
        result = await secundario.procesar(dato)

  BIEN — consumidor conoce solo el puerto:
    servicio = FallbackServicio(primary=..., secondary=...)
    result = await servicio.procesar(dato)

  Con el patron Composite, agregar un tercer proveedor
  solo cambia FallbackServicio — el consumidor no se entera.
""")


asyncio.run(main())
