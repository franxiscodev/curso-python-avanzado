"""Tests unitarios para pycommute.core.history."""

from pycommute.core.history import ConsultaHistory

WEATHER = {"city": "Valencia", "temperature": 22.0, "description": "clear sky"}
ROUTES = [{"profile": "cycling-regular", "distance_km": 2.0, "duration_min": 8}]


def test_history_add_and_retrieve() -> None:
    """Verifica que add() y get_recent() funcionan correctamente."""
    history = ConsultaHistory(maxlen=10)
    history.add("Valencia", ["cycling-regular"], WEATHER, ROUTES)

    assert len(history) == 1
    entries = history.get_recent()
    assert entries[0].city == "Valencia"
    assert entries[0].profiles == ["cycling-regular"]


def test_history_respects_maxlen() -> None:
    """Verifica que maxlen descarta entradas antiguas automáticamente."""
    history = ConsultaHistory(maxlen=3)

    for city in ["Valencia", "Madrid", "Barcelona", "Sevilla"]:
        history.add(city, ["cycling-regular"], WEATHER, ROUTES)

    assert len(history) == 3
    cities = [e.city for e in history.get_recent()]
    assert "Valencia" not in cities
    assert "Sevilla" in cities


def test_history_get_recent_newest_first() -> None:
    """Verifica que get_recent() devuelve la más reciente primero."""
    history = ConsultaHistory(maxlen=10)
    history.add("Valencia", ["cycling-regular"], WEATHER, ROUTES)
    history.add("Madrid", ["driving-car"], WEATHER, ROUTES)
    history.add("Barcelona", ["foot-walking"], WEATHER, ROUTES)

    entries = history.get_recent()
    assert entries[0].city == "Barcelona"
    assert entries[1].city == "Madrid"
    assert entries[2].city == "Valencia"
