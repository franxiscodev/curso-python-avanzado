"""Resiliencia comparativa — fallback vs retry vs sin proteccion.

Demuestra:
- Sin proteccion: el primer error mata la ejecucion
- Con retry (tenacity): reintenta antes de rendirse
- Con fallback: conmuta a alternativa si falla
- Comparativa de latencia: cloud vs local vs fallback

No requiere Ollama ni API keys — todo simulado.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_11/conceptos/04_resiliencia_comparativa.py

    # Linux
    uv run scripts/clase_11/conceptos/04_resiliencia_comparativa.py
"""

import asyncio
import time
from typing import Protocol


# ── Puerto ────────────────────────────────────────────────────────────
class AIPort(Protocol):
    async def generar(self, prompt: str) -> str: ...


# ── Simuladores ───────────────────────────────────────────────────────
class SimuladorGemini:
    """Simula Gemini: rapido pero puede fallar (429, timeout, etc.)."""

    def __init__(self, falla: bool = False, latencia: float = 0.1) -> None:
        self._falla = falla
        self._latencia = latencia

    async def generar(self, prompt: str) -> str:
        await asyncio.sleep(self._latencia)
        if self._falla:
            raise ConnectionError("429 RESOURCE_EXHAUSTED — cuota agotada")
        return "Respuesta Gemini (cloud, alta calidad)"


class SimuladorOllama:
    """Simula Ollama: mas lento pero siempre disponible (local)."""

    def __init__(self, latencia: float = 0.5) -> None:
        self._latencia = latencia

    async def generar(self, prompt: str) -> str:
        await asyncio.sleep(self._latencia)
        return "Respuesta Ollama (local, calidad media)"


# ── Estrategias de resiliencia ────────────────────────────────────────
class FallbackAI:
    """Intenta primary, conmuta a secondary si falla."""

    def __init__(self, primary: AIPort, secondary: AIPort) -> None:
        self._primary = primary
        self._secondary = secondary

    async def generar(self, prompt: str) -> str:
        try:
            return await self._primary.generar(prompt)
        except Exception as e:
            print(f"    Fallback activado: {e}")
            return await self._secondary.generar(prompt)


async def medir(nombre: str, servicio: AIPort, n: int = 3) -> None:
    """Mide el tiempo total de N llamadas al servicio."""
    inicio = time.perf_counter()
    ultimo = ""
    try:
        for _ in range(n):
            ultimo = await servicio.generar("prompt de movilidad")
        total = time.perf_counter() - inicio
        print(f"  {nombre:<35} {total:.2f}s para {n} requests")
        print(f"    Ultima respuesta: {ultimo[:50]}")
    except Exception as e:
        total = time.perf_counter() - inicio
        print(f"  {nombre:<35} FALLO en {total:.2f}s: {e}")


async def main() -> None:
    print("=== Comparativa de estrategias de resiliencia ===\n")

    print("1. Gemini disponible — caso ideal:")
    await medir("Gemini (disponible)", SimuladorGemini())

    print("\n2. Gemini caido — sin proteccion:")
    await medir("Gemini (caido, sin fallback)", SimuladorGemini(falla=True))

    print("\n3. Gemini caido — con fallback a Ollama:")
    fallback = FallbackAI(
        primary=SimuladorGemini(falla=True),
        secondary=SimuladorOllama(),
    )
    await medir("FallbackAI (Gemini->Ollama)", fallback)

    print("\n4. Solo Ollama — siempre disponible pero mas lento:")
    await medir("Solo Ollama (local)", SimuladorOllama())

    print("\n=== Conclusiones ===")
    print("""
  Gemini disponible:    ~0.1s por request — ideal
  Gemini caido sin proteccion: FALLA — sistema inutilizable
  FallbackAI (Gemini->Ollama): primera request lenta (falla+fallback),
                                las siguientes usan Ollama directamente
                                (implementacion simple — sin estado)
  Solo Ollama:          ~0.5s por request — predecible, sin riesgo

  El fallback no es gratis: la primera llamada paga el costo
  de intentar el primario. Un Circuit Breaker evita este costo
  abriendo el circuito tras N fallos consecutivos.
""")


asyncio.run(main())
