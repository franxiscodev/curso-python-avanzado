"""cProfile básico — medir antes de optimizar.

Demuestra cómo usar cProfile para identificar qué funciones
consumen más tiempo en un programa. Sin imports de pycommute.

Ejecutar:
    uv run scripts/clase_06/conceptos/01_cprofile_basico.py
"""

import cProfile
import io
import pstats
import time


def operacion_lenta() -> list[int]:
    """Simula una operación costosa (I/O, base de datos, API)."""
    time.sleep(0.1)
    return list(range(1000))


def operacion_rapida() -> int:
    """Simula una operación ligera."""
    return sum(range(100))


def programa_completo() -> dict:
    """Combina ambas operaciones."""
    datos = operacion_lenta()
    total = operacion_rapida()
    return {"datos": len(datos), "total": total}


# ── Perfilar con cProfile ────────────────────────────────────────
profiler = cProfile.Profile()
profiler.enable()
resultado = programa_completo()
profiler.disable()

# ── Mostrar resultados ordenados por tiempo acumulado ────────────
stream = io.StringIO()
stats = pstats.Stats(profiler, stream=stream)
stats.sort_stats("cumulative")  # cumtime: tiempo total incluyendo llamadas internas
stats.print_stats(5)            # top 5 funciones más lentas

print(stream.getvalue())
print(f"Resultado: {resultado}")
print()
print("Columnas del informe:")
print("  ncalls    — número de llamadas")
print("  tottime   — tiempo en la función (sin contar subcalls)")
print("  cumtime   — tiempo acumulado (función + todas las que llama)")
print("  filename  — archivo:línea(función)")
