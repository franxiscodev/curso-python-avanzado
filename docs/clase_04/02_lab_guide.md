# Lab Guide — Clase 4: Testing y Mocks

## ¿Por qué construimos esto así?

Elegimos `pytest-mock` en lugar de `unittest.mock` directamente porque encaja
mejor con la filosofía de pytest: todo es un fixture. Con `pytest-mock` el
objeto `mocker` llega como fixture a cada test, sin necesidad de decoradores
`@patch` que mezclan dos estilos distintos en el mismo archivo.

Los mocks de `httpx` se definen en `conftest.py` porque `test_weather.py` y
`test_route.py` los necesitan. Duplicarlos sería violar DRY en los propios
tests — exactamente lo que los tests deberían detectar en el código de
producción.

`_Settings` con `env_file=None` resuelve un problema concreto: `Settings`
llama a `get_settings()` que usa `@lru_cache`, y ese singleton se instancia al
importar el módulo. Si usáramos la clase real con `env_file=".env"`,
`monkeypatch` actuaría demasiado tarde. La clase local aislada garantiza que
cada test parte de cero, sin efectos entre tests.

No testeamos `@retry` en esta clase. Hacerlo correctamente requiere controlar
el tiempo y las excepciones de forma precisa — esas técnicas llegan en la
Clase 6.

---

## Dependencias de esta clase

```bash
# Windows (PowerShell) y Linux (idéntico)
uv add --dev pytest-mock
```

Verifica que `pyproject.toml` incluye `pytest-mock` bajo el comentario
`# Clase 4` en la sección `[dependency-groups]` o `[tool.pytest...]`.

---

## Pasos del lab

### Paso 1 — Instalar `pytest-mock`

```bash
# Windows (PowerShell) y Linux (idéntico)
uv add --dev "pytest-mock>=3.14"
```

Concepto aplicado: sección "pytest-mock y el fixture `mocker`" de
`01_conceptos.md`.

---

### Paso 2 — Reorganizar `conftest.py` con fixtures compartidas

Abre `curso/tests/conftest.py` y reemplaza los mocks que cada test definía
localmente por dos fixtures compartidas:

```python
import pytest

@pytest.fixture
def mock_httpx_weather(mocker):
    """Mock de httpx.Client para llamadas a OpenWeatherMap."""
    mock = mocker.patch("pycommute.weather.httpx.Client")
    # configura aquí el return_value según la forma real de la respuesta
    return mock

@pytest.fixture
def mock_httpx_route(mocker):
    """Mock de httpx.Client para llamadas a OpenRouteService."""
    mock = mocker.patch("pycommute.route.httpx.Client")
    # configura aquí el return_value según la forma real de la respuesta
    return mock
```

Concepto aplicado: sección "Fixtures en `conftest.py`" de `01_conceptos.md`.

> `mocker.patch()` apunta al módulo donde `httpx` se **usa**, no donde se
> define — `pycommute.weather.httpx`, no `httpx.Client`.

---

### Paso 3 — Expandir `test_weather.py` a 5 tests

Aplicamos la sección "Tipos de asserts y verificación de contratos" de
`01_conceptos.md`.

Los cinco tests que debe contener `curso/tests/unit/test_weather.py`:

1. **Respuesta válida devuelve datos correctos** — ya existía en Clase 3.
2. **Error HTTP lanza excepción** — ya existía en Clase 3.
3. **Check de tipos** — verifica que la función devuelve `dict` y que los
   campos clave (`temp`, `description`) son del tipo esperado.
4. **Respuesta malformada** — cuando el JSON no contiene los campos esperados,
   la función lanza la excepción adecuada en lugar de devolver `None`
   silenciosamente.
5. **Parametrize: 3 ciudades** — el mismo comportamiento correcto para
   `"Madrid"`, `"Valencia"` y `"Bilbao"`.

Estructura del test parametrizado:

```python
import pytest

@pytest.mark.parametrize("city", ["Madrid", "Valencia", "Bilbao"])
def test_weather_multiple_cities(city, mock_httpx_weather):
    result = get_weather(city, api_key="test-key")
    assert isinstance(result, dict)
    assert "temp" in result
```

---

### Paso 4 — Expandir `test_route.py` a 5 tests

Aplicamos la sección "Parametrize y casos edge" de `01_conceptos.md`.

Los cinco tests que debe contener `curso/tests/unit/test_route.py`:

1. **Respuesta válida devuelve datos correctos** — ya existía en Clase 3.
2. **Error HTTP lanza excepción** — ya existía en Clase 3.
3. **Conversión de unidades** — verifica que la distancia en metros se
   convierte correctamente a kilómetros en el resultado devuelto.
4. **Profile preservado** — el campo `profile` del resultado coincide con el
   argumento pasado a la función (`"foot-walking"`, `"driving-car"`, etc.).
5. **Parametrize: 3 perfiles** — el mismo comportamiento correcto para
   `"foot-walking"`, `"driving-car"` y `"cycling-regular"`.

Estructura del test parametrizado:

```python
@pytest.mark.parametrize("profile", ["foot-walking", "driving-car", "cycling-regular"])
def test_route_multiple_profiles(profile, mock_httpx_route):
    result = get_route(origin=(40.4, -3.7), destination=(39.5, -0.4), profile=profile)
    assert result["profile"] == profile
```

---

### Paso 5 — Crear `test_config.py` con `_Settings` aislada

Crea `curso/tests/unit/test_config.py`. La clave de diseño es usar una clase
local `_Settings` con `env_file=None` para aislar cada test del `.env` real y
del singleton de `get_settings()`.

Concepto aplicado: sección "`monkeypatch` y aislamiento de entorno" de
`01_conceptos.md`.

Los tres tests:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytest

class _Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None)
    openweather_api_key: str
    openrouteservice_api_key: str
    app_name: str = "pycommute"

def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "ow-test")
    monkeypatch.setenv("OPENROUTESERVICE_API_KEY", "ors-test")
    s = _Settings()
    assert s.openweather_api_key == "ow-test"
    assert s.openrouteservice_api_key == "ors-test"

def test_settings_raises_without_required_keys(monkeypatch):
    from pydantic import ValidationError
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTESERVICE_API_KEY", raising=False)
    with pytest.raises(ValidationError):
        _Settings()

def test_settings_default_values(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "ow-test")
    monkeypatch.setenv("OPENROUTESERVICE_API_KEY", "ors-test")
    s = _Settings()
    assert s.app_name == "pycommute"
```

> Si tu `Settings` real tiene campos opcionales con defaults distintos,
> ajusta `_Settings` para que refleje exactamente los mismos campos y valores.

---

### Paso 6 — Verificar el hito: 17 tests en verde

```bash
# Windows (PowerShell)
uv run pytest tests/ -v

# Linux
uv run pytest tests/ -v
```

Salida esperada:

```
tests/unit/test_weather.py::test_weather_valid_response PASSED
tests/unit/test_weather.py::test_weather_http_error PASSED
tests/unit/test_weather.py::test_weather_returns_dict PASSED
tests/unit/test_weather.py::test_weather_malformed_response PASSED
tests/unit/test_weather.py::test_weather_multiple_cities[Madrid] PASSED
tests/unit/test_weather.py::test_weather_multiple_cities[Valencia] PASSED
tests/unit/test_weather.py::test_weather_multiple_cities[Bilbao] PASSED
tests/unit/test_route.py::test_route_valid_response PASSED
tests/unit/test_route.py::test_route_http_error PASSED
tests/unit/test_route.py::test_route_unit_conversion PASSED
tests/unit/test_route.py::test_route_profile_preserved PASSED
tests/unit/test_route.py::test_route_multiple_profiles[foot-walking] PASSED
tests/unit/test_route.py::test_route_multiple_profiles[driving-car] PASSED
tests/unit/test_route.py::test_route_multiple_profiles[cycling-regular] PASSED
tests/unit/test_config.py::test_settings_loads_from_env PASSED
tests/unit/test_config.py::test_settings_raises_without_required_keys PASSED
tests/unit/test_config.py::test_settings_default_values PASSED

17 passed in 0.32s
```

Si ves 17 tests en verde, el hito está completo.

---

## Hito de la Clase 4

Tu suite de tests al terminar esta clase debe coincidir con
`curso/snapshots/clase_04/tests/`.

```bash
# Windows (PowerShell)
uv run pytest tests/ -v

# Linux
uv run pytest tests/ -v
```

Compara tu `tests/` con `snapshots/clase_04/tests/` para verificar que la
estructura de fixtures, la organización de `conftest.py` y la cobertura de
casos coinciden con el hito documentado.

La Clase 5 toma esta suite como base para agregar tests de concurrencia con
`anyio` — por eso es importante que todos los mocks pasen por `conftest.py` y
no queden dispersos en cada archivo de test.
