"""
Ejercicios — Clase 11: IA Local con Ollama y Patrón Fallback
=============================================================
Cuatro ejercicios sobre resiliencia, patrón fallback y composición de proveedores.

Ejecutar (desde curso/):
    uv run python scripts/clase_11/ejercicios_clase_11.py

Requisito: autocontenido, sin imports de pycommute.
Sin llamadas reales a Ollama — se usan funciones simuladas que lanzan excepciones.
"""

from typing import Any, Callable, Optional


# ---------------------------------------------------------------------------
# Proveedores simulados ya implementados — no modificar
# ---------------------------------------------------------------------------

def proveedor_falla() -> str:
    """Siempre lanza una excepción (simula proveedor caído)."""
    raise ConnectionError("Proveedor no disponible")


def proveedor_lento() -> str:
    """Siempre lanza TimeoutError (simula proveedor lento)."""
    raise TimeoutError("Tiempo de espera agotado")


def proveedor_ok() -> str:
    """Siempre tiene éxito (simula proveedor funcional)."""
    return "Respuesta del proveedor funcional."


def proveedor_ok_alternativo() -> str:
    """Proveedor alternativo funcional."""
    return "Respuesta del proveedor alternativo."


_INTENTOS_CONTADOR: list[int] = [0]


def proveedor_intermitente() -> str:
    """Falla las primeras 2 llamadas, tiene éxito a partir de la 3ª."""
    _INTENTOS_CONTADOR[0] += 1
    if _INTENTOS_CONTADOR[0] < 3:
        raise RuntimeError(f"Fallo intento #{_INTENTOS_CONTADOR[0]}")
    return f"Éxito en el intento #{_INTENTOS_CONTADOR[0]}"


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Función con_fallback: llama primaria, usa fallback si falla
# Implementa `con_fallback(primaria: Callable[[], str], valor_fallback: str) -> str`
# Debe:
#   - Llamar a primaria()
#   - Si lanza cualquier Exception, retornar valor_fallback
#   - Si tiene éxito, retornar el resultado
# Pista: sección 4 (Patrón Fallback con reintentos) en 01_conceptos.md — bloque try/except de orchestrate_ai
def con_fallback(primaria: Callable[[], str], valor_fallback: str) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — Clase LLMCompuesto con lista de proveedores
# Implementa la clase `LLMCompuesto` con:
#   - __init__(self, proveedores: list[Callable[[], str]]) -> None
#     que guarda los proveedores en self._proveedores
#   - generar(self, prompt: str) -> str
#     que intenta cada proveedor en orden, retorna el primer resultado exitoso,
#     si todos fallan lanza RuntimeError("Todos los proveedores fallaron")
# Nota: el parámetro `prompt` se ignora en este ejercicio (los proveedores son callables sin args)
# Pista: sección 4 (Patrón Fallback con reintentos) en 01_conceptos.md — orchestrate_ai con múltiples proveedores
class LLMCompuesto:
    def __init__(self, proveedores: list[Callable[[], str]]) -> None:
        pass  # ← reemplazar con tu implementación

    def generar(self, prompt: str) -> str:
        pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — con_reintento_timeout: reintenta ante TimeoutError
# Implementa `con_reintento_timeout(fn: Callable[[], str], max_intentos: int) -> str`
# Debe:
#   - Llamar a fn() hasta max_intentos veces
#   - Si la excepción es TimeoutError, reintentar
#   - Si es otro tipo de excepción, relanzarla inmediatamente (no reintentar)
#   - Si se agotan todos los intentos con TimeoutError, retornar "timeout"
# Pista: sección 4 (Patrón Fallback con reintentos) en 01_conceptos.md — retry_if_exception_type en tenacity
def con_reintento_timeout(fn: Callable[[], str], max_intentos: int) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 4
# ---------------------------------------------------------------------------

# TODO: Ejercicio 4 — cadena_fallback: prueba N proveedores, falla si todos fallan
# Implementa `cadena_fallback(*proveedores: Callable[[], str]) -> str`
# Debe:
#   - Aceptar un número variable de callables
#   - Probar cada uno en orden
#   - Retornar el resultado del primero que tenga éxito
#   - Si todos fallan, lanzar RuntimeError("Todos los proveedores fallaron")
# Diferencia con LLMCompuesto: es una función, no una clase, y no acepta prompt
# Pista: sección 4 (Patrón Fallback con reintentos) en 01_conceptos.md — variación del patrón con *args
def cadena_fallback(*proveedores: Callable[[], str]) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo — muestra los resultados (no modificar)
# ---------------------------------------------------------------------------

def demo() -> None:
    print("=== Ejercicio 1: con_fallback ===")
    resultado_ok = con_fallback(proveedor_ok, "valor_de_emergencia")
    resultado_caido = con_fallback(proveedor_falla, "valor_de_emergencia")
    if resultado_ok is not None:
        print(f"  Proveedor ok: {resultado_ok}")
        print(f"  Proveedor caido -> fallback: {resultado_caido}")
    else:
        print("  Sin implementar aún.")

    print("\n=== Ejercicio 2: LLMCompuesto ===")
    try:
        llm = LLMCompuesto([proveedor_falla, proveedor_lento, proveedor_ok])
        resp = llm.generar("¿Qué tiempo hace?")
        if resp is not None:
            print(f"  Respuesta: {resp}")
        else:
            print("  Sin implementar aún.")
    except Exception as e:
        print(f"  Error inesperado: {e}")

    print("\n=== Ejercicio 3: con_reintento_timeout ===")
    resultado_timeout = con_reintento_timeout(proveedor_lento, max_intentos=3)
    if resultado_timeout is not None:
        print(f"  TimeoutError agotado -> '{resultado_timeout}'")
    else:
        print("  Sin implementar aún.")
    try:
        con_reintento_timeout(proveedor_falla, max_intentos=3)
    except ConnectionError as e:
        print(f"  ConnectionError relanzado correctamente: {e}")
    except Exception:
        print("  Sin implementar aún.")

    print("\n=== Ejercicio 4: cadena_fallback ===")
    resultado = cadena_fallback(proveedor_falla, proveedor_lento, proveedor_ok_alternativo)
    if resultado is not None:
        print(f"  Resultado: {resultado}")
    else:
        print("  Sin implementar aún.")
    try:
        cadena_fallback(proveedor_falla, proveedor_lento)
    except RuntimeError as e:
        print(f"  Todos fallaron -> RuntimeError: {e}")
    except Exception:
        print("  Sin implementar aún.")


if __name__ == "__main__":
    demo()
