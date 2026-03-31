"""
Ejercicios — Clase 04: Testing Profesional con pytest
======================================================
Cuatro ejercicios para practicar fixtures, parametrize, mocks y excepciones.

NOTA: Este archivo contiene tests de pytest.
Ejecutar (desde curso/):
    uv run pytest scripts/clase_04/ejercicios_clase_04.py -v

Requisito: autocontenido, sin imports de pycommute.
"""

import pytest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Funciones de producción (ya implementadas — no modificar)
# ---------------------------------------------------------------------------

def calcular_descuento(precio: float, porcentaje: float) -> float:
    """Aplica un descuento porcentual a un precio."""
    if porcentaje < 0 or porcentaje > 100:
        raise ValueError(f"Porcentaje inválido: {porcentaje}")
    return round(precio * (1 - porcentaje / 100), 2)


def obtener_temperatura_ciudad(ciudad: str, cliente_http) -> float:
    """Llama a cliente_http.get(ciudad) y retorna la temperatura."""
    respuesta = cliente_http.get(ciudad)
    return respuesta["temp"]


def dividir(a: float, b: float) -> float:
    """Divide a entre b."""
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero")
    return a / b


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Fixture simple
# Crea una fixture llamada `datos_clima` decorada con @pytest.fixture que
# retorne el siguiente dict:
#   {
#       "ciudad": "Valencia",
#       "temp": 22.5,
#       "humedad": 65,
#       "descripcion": "cielo despejado"
#   }
# Luego escribe un test `test_datos_clima_tiene_ciudad` que use la fixture
# y verifique que datos_clima["ciudad"] == "Valencia".
# Pista: repasa "Fixtures" en 01_conceptos.md

# --- escribe aquí la fixture y el test ---


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — pytest.mark.parametrize con 3 casos
# Escribe un test `test_calcular_descuento` decorado con @pytest.mark.parametrize
# que pruebe `calcular_descuento` con estos 3 casos:
#   (precio=100.0, porcentaje=10.0, esperado=90.0)
#   (precio=50.0,  porcentaje=50.0, esperado=25.0)
#   (precio=200.0, porcentaje=0.0,  esperado=200.0)
# Pista: repasa "pytest.mark.parametrize" en 01_conceptos.md

# --- escribe aquí el test parametrizado ---


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — Mock de función externa con mocker.patch
# Escribe un test `test_obtener_temperatura_con_mock` que:
#   1. Crea un MagicMock() llamado `cliente_falso`
#   2. Configura cliente_falso.get.return_value = {"temp": 18.0, "ciudad": "Madrid"}
#   3. Llama a `obtener_temperatura_ciudad("Madrid", cliente_falso)`
#   4. Verifica que el resultado es 18.0
#   5. Verifica que cliente_falso.get fue llamado con "Madrid"
# No uses mocker.patch — aquí bastará con MagicMock directamente.
# Pista: repasa "Mocks y MagicMock" en 01_conceptos.md

# --- escribe aquí el test con mock ---


# ---------------------------------------------------------------------------
# Ejercicio 4
# ---------------------------------------------------------------------------

# TODO: Ejercicio 4 — Test que verifica excepciones con pytest.raises
# Escribe DOS tests usando pytest.raises:
#   a) `test_dividir_por_cero` — verifica que dividir(10, 0) lanza ZeroDivisionError
#      y que el mensaje contiene "cero"
#   b) `test_descuento_invalido` — verifica que calcular_descuento(100, -5) lanza
#      ValueError y que el mensaje contiene "inválido"
# Pista: repasa "pytest.raises y verificación de excepciones" en 01_conceptos.md

# --- escribe aquí los dos tests de excepciones ---
