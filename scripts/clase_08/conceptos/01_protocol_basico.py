"""Concepto 01 — typing.Protocol: contratos sin herencia.

Un Protocol define QUE metodos debe tener un objeto, sin obligar a heredar.
Duck typing estructural: si camina como pato y grazna como pato, es un pato.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_08/conceptos/01_protocol_basico.py

    # Linux
    uv run scripts/clase_08/conceptos/01_protocol_basico.py
"""

from typing import Protocol, runtime_checkable


# --- Definicion del Protocol ---

@runtime_checkable
class Describible(Protocol):
    """Cualquier objeto que tenga un metodo describe() es Describible."""

    def describe(self) -> str:
        ...


# --- Implementaciones concretas (sin herencia) ---

class Perro:
    def describe(self) -> str:
        return "Soy un perro"


class Gato:
    def describe(self) -> str:
        return "Soy un gato"


class Piedra:
    pass  # No tiene describe() — NO satisface el Protocol


# --- Funcion que acepta cualquier Describible ---

def imprimir_descripcion(obj: Describible) -> None:
    print(f"  Descripcion: {obj.describe()}")


# --- Demo ---

print("=== isinstance con @runtime_checkable ===")
perro = Perro()
gato = Gato()
piedra = Piedra()

print(f"Perro satisface Describible:  {isinstance(perro, Describible)}")   # True
print(f"Gato satisface Describible:   {isinstance(gato, Describible)}")    # True
print(f"Piedra satisface Describible: {isinstance(piedra, Describible)}")  # False

print()
print("=== Uso polimórfico sin herencia ===")
for animal in [perro, gato]:
    imprimir_descripcion(animal)

# Sin herencia = sin acoplamiento
# Perro y Gato pueden existir en librerias distintas
# y seguir siendo intercambiables aqui
print()
print("Perro y Gato NO heredan de Describible ni entre si.")
print("El Protocol solo describe la forma, no impone jerarquia.")
