"""
cProfile — Medir antes de optimizar
=====================================
Demuestra cómo usar cProfile para identificar qué funciones consumen
más tiempo en un programa. Caso real: validación masiva de usuarios
con Pydantic, un patrón típico en adaptadores de PyCommute.

Conceptos que ilustra:
- cProfile.Profile(): profiler determinístico que instrumenta cada llamada.
- pstats.sort_stats('tottime'): ordena por tiempo propio de la función,
  sin contar el tiempo de sus subcalls. Identifica el cuello de botella real.
- stats.print_stats(5): muestra solo el Top 5 de funciones más costosas.

Requiere: email-validator (uv add --dev email-validator)

Ejecutar:
    uv run python scripts/clase_06/conceptos/01_cprofile_basico.py
"""
import pstats
from pydantic import BaseModel, EmailStr
import cProfile

# 1. Definimos nuestro modelo de contrato (Capa de Dominio)


class CommuteUser(BaseModel):
    id: int
    name: str
    email: EmailStr


def procesar_usuarios_legacy(datos_crudos: list[dict]):
    """Simula un adaptador ineficiente que procesa una lista enorme."""
    usuarios_validos = []
    for raw in datos_crudos:
        # El cuello de botella: Instanciar y validar Pydantic miles de veces en un loop
        user = CommuteUser(**raw)
        usuarios_validos.append(user)
    return usuarios_validos


def main():
    # Generamos 50,000 registros falsos
    payload_masivo = [
        {"id": i, "name": f"User {i}", "email": f"user{i}@pycommute.com"}
        for i in range(50_000)
    ]
    procesar_usuarios_legacy(payload_masivo)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()

    # Ordenamos por el tiempo acumulado (tottime) para ver qué función duele más
    stats = pstats.Stats(profiler).sort_stats('tottime')
    stats.print_stats(5)  # Mostramos solo el Top 5
