"""Concepto 03 — Regla de Dependencia: el nucleo no depende de la infraestructura.

En Arquitectura Hexagonal las dependencias apuntan HACIA ADENTRO:
- Adaptadores dependen de Puertos (core)
- El servicio (core) no sabe nada de httpx, bases de datos ni APIs externas

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_08/conceptos/03_regla_dependencia.py

    # Linux
    uv run scripts/clase_08/conceptos/03_regla_dependencia.py
"""

from typing import Protocol


# ┌─────────────────────────────────────────────────────────────────────┐
# │  NUCLEO (core) — solo logica de negocio, cero imports externos      │
# └─────────────────────────────────────────────────────────────────────┘

class TemperaturaPort(Protocol):
    """Puerto: contrato que el nucleo define."""
    def obtener_celsius(self, ciudad: str) -> float:
        ...


class AlertaClimatica:
    """Logica de negocio pura — depende del Puerto, no del adaptador."""

    UMBRAL_FRIO = 5.0
    UMBRAL_CALOR = 35.0

    def __init__(self, temperatura: TemperaturaPort) -> None:
        self._temperatura = temperatura

    def evaluar(self, ciudad: str) -> str:
        temp = self._temperatura.obtener_celsius(ciudad)
        if temp < self.UMBRAL_FRIO:
            return f"FRIO EXTREMO en {ciudad}: {temp}C"
        if temp > self.UMBRAL_CALOR:
            return f"CALOR EXTREMO en {ciudad}: {temp}C"
        return f"Temperatura normal en {ciudad}: {temp}C"


# ┌─────────────────────────────────────────────────────────────────────┐
# │  ADAPTADORES — implementan el Puerto, conocen el mundo exterior     │
# └─────────────────────────────────────────────────────────────────────┘

class TemperaturaFake:
    """Adaptador fake — datos hardcodeados para demo sin HTTP."""

    _DATOS = {"Madrid": 38.5, "Valencia": 22.0, "Bilbao": 3.2}

    def obtener_celsius(self, ciudad: str) -> float:
        return self._DATOS.get(ciudad, 20.0)


class TemperaturaFija:
    """Adaptador configurable — util en tests unitarios."""

    def __init__(self, valor: float) -> None:
        self._valor = valor

    def obtener_celsius(self, ciudad: str) -> float:
        return self._valor


# --- Demo ---

print("=== Regla de Dependencia ===")
print()
print("AlertaClimatica (nucleo) NUNCA importa httpx, requests ni nada externo.")
print("Solo conoce TemperaturaPort — el adaptador lo elige quien llama.")
print()

alerta = AlertaClimatica(temperatura=TemperaturaFake())

for ciudad in ["Madrid", "Valencia", "Bilbao"]:
    resultado = alerta.evaluar(ciudad)
    print(f"  {resultado}")

print()
print("=== Cambiar adaptador sin tocar la logica ===")
alerta_test = AlertaClimatica(temperatura=TemperaturaFija(-10.0))
print(f"  {alerta_test.evaluar('CualquierCiudad')}")

alerta_test2 = AlertaClimatica(temperatura=TemperaturaFija(40.0))
print(f"  {alerta_test2.evaluar('CualquierCiudad')}")

print()
print("El nucleo no cambio — solo el adaptador.")
print("Esto es la Regla de Dependencia aplicada.")
