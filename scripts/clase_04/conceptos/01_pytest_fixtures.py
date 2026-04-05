"""Fixtures en pytest: escenarios nombrados y reutilizables.

Demuestra el patrón de fixtures con tres escenarios para validate_route_payload():
- valid_route: el happy path — datos correctos, la funcion retorna True
- invalid_route_negative: sad path — distancia negativa, logicamente imposible
- invalid_route_incomplete: sad path — clave faltante, estructura corrupta

Cada fixture define UN estado concreto que pytest inyecta por nombre.
pytest.raises(ValueError, match="...") verifica tipo de excepcion Y mensaje.

Ejecutar (desde curso/):
    uv run pytest scripts/clase_04/conceptos/01_pytest_fixtures.py -v
"""

import pytest

# --- 1. NUESTRA LÓGICA DE NEGOCIO ---


def validate_route_payload(payload: dict) -> bool:
    """Valida un diccionario de ruta. Lanza ValueError si es inválido."""
    if "distancia_km" not in payload:
        raise ValueError("Payload corrupto: falta la clave 'distancia_km'")

    if payload["distancia_km"] <= 0:
        raise ValueError(
            "Violación de dominio: La distancia debe ser mayor a 0")

    return True

# --- 2. NUESTRO ARSENAL DE FIXTURES ---
# Tres fixtures = tres escenarios. Cada una tiene un nombre que describe
# el estado que representa — no "datos_test_1", sino "invalid_route_negative".


@pytest.fixture
def valid_route() -> dict:
    """Fixture: Escenario ideal — todos los campos presentes y válidos."""
    return {"origen": "Madrid", "destino": "Valencia", "distancia_km": 350}


@pytest.fixture
def invalid_route_negative() -> dict:
    """Fixture: Escenario de fallo — distancia lógicamente imposible."""
    return {"origen": "Madrid", "destino": "Valencia", "distancia_km": -15}


@pytest.fixture
def invalid_route_incomplete() -> dict:
    """Fixture: Escenario de fallo — estructura corrupta, clave faltante."""
    return {"origen": "Madrid", "destino": "Valencia"}

# --- 3. NUESTROS TESTS ---

# Happy Path


def test_validation_passes_with_correct_data(valid_route: dict):
    # pytest inyecta valid_route por nombre — sin import, sin instanciar
    assert validate_route_payload(valid_route) is True

# Sad Path 1: Validar el valor numérico


def test_validation_fails_with_negative_distance(invalid_route_negative: dict):
    # match= es una regex: el test PASA solo si ValueError Y el mensaje
    # contiene exactamente "Violación de dominio"
    with pytest.raises(ValueError, match="Violación de dominio"):
        validate_route_payload(invalid_route_negative)

# Sad Path 2: Validar la estructura del diccionario


def test_validation_fails_with_missing_keys(invalid_route_incomplete: dict):
    # Distinto match= que el test anterior — cada error tiene su propio mensaje
    with pytest.raises(ValueError, match="Payload corrupto"):
        validate_route_payload(invalid_route_incomplete)
