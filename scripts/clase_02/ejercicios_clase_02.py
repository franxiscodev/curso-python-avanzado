"""
Ejercicios — Clase 02: Structural Pattern Matching
====================================================
Cuatro ejercicios para practicar match/case sobre distintas estructuras.

Ejecutar:
    uv run python scripts/clase_02/ejercicios_clase_02.py

Requisito: autocontenido, sin imports de pycommute.
"""

from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — match/case sobre tipos primitivos
# Implementa `clasificar_valor` que recibe un valor `Any` y retorna un str:
#   - Si es None          → "nulo"
#   - Si es True o False  → "booleano: True" o "booleano: False"
#   - Si es int           → "entero: <valor>"
#   - Si es str vacío     → "cadena vacía"
#   - Si es str           → "cadena: <valor>"
#   - Para cualquier otro → "desconocido"
# Pista: repasa "Patrones de valor y captura" en 01_conceptos.md
def clasificar_valor(valor: Any) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — match/case sobre dicts con guard clauses
# Implementa `interpretar_clima` que recibe un dict con clave "temp" (float)
# y retorna un str según la temperatura:
#   - temp > 35       → "calor extremo"
#   - temp > 25       → "calor agradable"
#   - temp > 15       → "templado"
#   - temp > 5        → "fresco"
#   - cualquier otro  → "frío"
# Usar match/case con guard clauses (if) sobre el dict.
# Pista: repasa "Patrones de mapping (dicts)" en 01_conceptos.md
def interpretar_clima(datos: dict) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — match/case sobre listas
# Implementa `describir_lista` que recibe una lista y retorna un str:
#   - Lista vacía             → "lista vacía"
#   - Lista con un elemento   → "un elemento: <elemento>"
#   - Lista con dos elementos → "dos elementos: <elem1> y <elem2>"
#   - Lista con más elementos → "lista de <n> elementos, primero: <primer_elem>"
# Pista: repasa "Patrones de secuencia (listas/tuplas)" en 01_conceptos.md
def describir_lista(items: list) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Clases de apoyo para Ejercicio 4
# ---------------------------------------------------------------------------

@dataclass
class Tren:
    linea: str
    destino: str
    retraso_min: int = 0


@dataclass
class Bus:
    numero: str
    destino: str


@dataclass
class Metro:
    linea: str
    direccion: str


# ---------------------------------------------------------------------------
# Ejercicio 4
# ---------------------------------------------------------------------------

# TODO: Ejercicio 4 — match/case con clases (dataclasses)
# Implementa `anunciar_transporte` que recibe un objeto que puede ser
# Tren, Bus o Metro, y retorna un str:
#   - Tren con retraso > 0: "Tren {linea} a {destino} — retraso: {retraso_min} min"
#   - Tren sin retraso:     "Tren {linea} a {destino} — a tiempo"
#   - Bus:                  "Bus {numero} dirección {destino}"
#   - Metro:                "Metro línea {linea} — {direccion}"
#   - Otro:                 "transporte desconocido"
# Pista: repasa "Patrones de clase" en 01_conceptos.md
def anunciar_transporte(transporte: Any) -> str:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo() -> None:
    print("=== Ejercicio 1: clasificar_valor ===")
    for v in [None, True, False, 42, "", "hola", 3.14]:
        resultado = clasificar_valor(v)
        print(f"  {v!r:12} → {resultado}")

    print("\n=== Ejercicio 2: interpretar_clima ===")
    for temp in [38.0, 28.0, 20.0, 10.0, 2.0]:
        resultado = interpretar_clima({"temp": temp})
        print(f"  {temp}°C → {resultado}")

    print("\n=== Ejercicio 3: describir_lista ===")
    for lista in [[], ["solo"], ["a", "b"], ["x", "y", "z", "w"]]:
        resultado = describir_lista(lista)
        print(f"  {lista} → {resultado}")

    print("\n=== Ejercicio 4: anunciar_transporte ===")
    transportes = [
        Tren("C1", "Madrid", retraso_min=5),
        Tren("AVE", "Barcelona"),
        Bus("47", "Aeropuerto"),
        Metro("L5", "Alameda"),
    ]
    for t in transportes:
        resultado = anunciar_transporte(t)
        print(f"  {resultado}")


if __name__ == "__main__":
    demo()
