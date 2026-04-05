"""El test integrador: fixtures + parametrize + mocker en un unico test.

Demuestra como los tres patrones se combinan para cubrir toda la logica
de recomendacion con 4 tests independientes sin llamadas reales a la red:

- eco_user_profile (fixture): define el estado base del usuario (has_car=False)
- parametrize: inyecta 4 condiciones climaticas distintas en cada test
- mocker.patch: reemplaza httpx.get por un mock que devuelve el clima del parametrize

Resultado: 4 tests que verifican cada rama del if/elif/else de la funcion.
La fixture y el parametrize cambian en cada ejecucion — el mock los conecta.

Ejecutar (desde curso/):
    uv run pytest scripts/clase_04/conceptos/04_commute_integrator.py -v
"""

import pytest
import httpx

# --- 1. NUESTRA LÓGICA DE NEGOCIO (Caso de Uso) ---


def get_commute_recommendation(origen: str, user_profile: dict) -> str:
    """Decide el mejor transporte basado en el clima y el usuario."""
    # Llamada externa a la red (El peligro a aislar)
    response = httpx.get(f"https://api.weather.com/v1/{origen}")
    weather_condition = response.json().get("condition", "Unknown")

    # Lógica de dominio core
    if weather_condition == "Rain" and not user_profile.get("has_car"):
        return "Take the Train"
    elif weather_condition == "Sunny":
        return "Ride a Bike"
    else:
        return "Take the Bus"

# --- 2. NUESTRO ESTADO BASE (Fixture) ---


@pytest.fixture
def eco_user_profile() -> dict:
    """Perfil de usuario que usaremos para este bloque de pruebas."""
    return {"name": "Alex", "has_car": False, "preferences": "eco"}

# --- 3. NUESTRO TEST INTEGRADOR ---


@pytest.mark.parametrize(
    "clima_simulado, recomendacion_esperada",
    [
        ("Sunny",    "Ride a Bike"),   # Rama elif — solo clima importa
        ("Rain",     "Take the Train"),# Rama if — depende de has_car=False de la fixture
        ("Snow",     "Take the Bus"),  # Rama else — valor no mapeado -> fallback
        ("Hurricane","Take the Bus"),  # Edge case extremo -> mismo fallback
    ]
)
def test_recommendation_engine_adapts_to_weather(
    mocker,
    eco_user_profile,
    clima_simulado,
    recomendacion_esperada
):
    # A. PREPARACIÓN — el clima viene del parametrize, el mock lo inyecta en la función
    mock_get = mocker.patch("httpx.get")
    mock_get.return_value.json.return_value = {"condition": clima_simulado}

    # B. EJECUCIÓN — eco_user_profile (has_car=False) se inyecta desde la fixture
    resultado = get_commute_recommendation("Madrid", eco_user_profile)

    # C. VALIDACIÓN — resultado + que se llamó a la URL correcta
    assert resultado == recomendacion_esperada
    mock_get.assert_called_once_with("https://api.weather.com/v1/Madrid")
