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


@pytest.fixture
def valid_route() -> dict:
    """Fixture: Escenario ideal."""
    return {"origen": "Madrid", "destino": "Valencia", "distancia_km": 350}


@pytest.fixture
def invalid_route_negative() -> dict:
    """Fixture: Escenario de fallo - Datos lógicamente imposibles."""
    return {"origen": "Madrid", "destino": "Valencia", "distancia_km": -15}


@pytest.fixture
def invalid_route_incomplete() -> dict:
    """Fixture: Escenario de fallo - Estructura mutilada."""
    return {"origen": "Madrid", "destino": "Valencia"}

# --- 3. NUESTROS TESTS ---

# Happy Path


def test_validation_passes_with_correct_data(valid_route: dict):
    # Inyectamos el diccionario perfecto
    assert validate_route_payload(valid_route) is True

# Sad Path 1: Validar el valor numérico


def test_validation_fails_with_negative_distance(invalid_route_negative: dict):
    # El test PASARÁ solo si la función lanza EXACTAMENTE un ValueError
    # y el mensaje contiene el texto indicado en 'match'.
    with pytest.raises(ValueError, match="Violación de dominio"):
        validate_route_payload(invalid_route_negative)

# Sad Path 2: Validar la estructura del diccionario


def test_validation_fails_with_missing_keys(invalid_route_incomplete: dict):
    # Inyectamos el diccionario mutilado
    with pytest.raises(ValueError, match="Payload corrupto"):
        validate_route_payload(invalid_route_incomplete)
