# Clase 04 — Testing Profesional con pytest

---

## 1. ¿Por qué testear?

Escribir tests no es trabajo extra: es la forma de trabajar sin miedo.

### El costo de no tener tests

Sin tests automatizados, cada cambio es un riesgo. Un refactor de una función central
puede romper cinco comportamientos distintos, y solo te enteras cuando un usuario
reporta el error en producción. Ese ciclo —cambio → deploy → bug → parche— es lento,
costoso y desgastante.

Con tests, el ciclo cambia: cambio → test falla → arreglas antes de salir. Los bugs
se detectan en segundos, no en días.

### CI/CD: tests que se ejecutan en cada push

En un flujo de integración continua, los tests corren automáticamente en cada push.
Si algo se rompe, el pipeline falla antes de que el código llegue a producción.

### Velocidad: unitarios vs integración

Un test que llama a una API real puede tardar 2-3 segundos. Con mocks, la misma
lógica se verifica en milisegundos:

- Tests **unitarios**: sin red, sin disco. Rápidos y deterministas. Usan mocks.
- Tests **de integración**: con dependencias reales. Lentos, pero verifican que las
  piezas encajan.

En esta clase nos centramos en los unitarios. La sección siguiente muestra el patrón
fundamental: fixtures para organizar escenarios, mocks para aislar dependencias.

---

## 2. Fixtures con pytest

### Qué es una fixture

Una fixture es una función decorada con `@pytest.fixture` que proporciona estado
a los tests. pytest la inyecta por nombre — no hace falta importarla ni instanciarla.

```python
import pytest

@pytest.fixture
def perfil_usuario() -> dict:
    return {"nombre": "Ana", "has_car": False, "ciudad": "Valencia"}

def test_perfil_tiene_nombre(perfil_usuario: dict):
    assert perfil_usuario["nombre"] == "Ana"
```

pytest detecta que `test_perfil_tiene_nombre` necesita `perfil_usuario` (por el
nombre del parámetro), ejecuta la fixture, y pasa el resultado al test.

### Organizar escenarios: happy path y sad path

El poder de las fixtures no está en una sola función — está en tener fixtures
para cada escenario relevante:

```python
@pytest.fixture
def ruta_valida() -> dict:
    return {"origen": "Madrid", "destino": "Valencia", "distancia_km": 350}

@pytest.fixture
def ruta_sin_destino() -> dict:
    return {"origen": "Madrid", "distancia_km": 350}  # campo faltante
```

Cada fixture tiene un nombre que describe el estado que representa. Los tests
los consumen directamente y son legibles sin contexto adicional.

### pytest.raises para verificar excepciones

`pytest.raises(TipoExcepcion, match="regex")` verifica dos cosas a la vez:
que se lanzó la excepción correcta Y que el mensaje contiene el patrón indicado.

```python
def test_ruta_sin_destino_lanza_error(ruta_sin_destino: dict):
    with pytest.raises(ValueError, match="campo faltante"):
        validate_route_payload(ruta_sin_destino)
```

Si la función no lanza nada, el test falla. Si lanza ValueError con un mensaje
distinto, también falla. Ambos contratos verificados en una línea.

---

▶ Ejecuta el ejemplo:
  uv run pytest scripts/clase_04/conceptos/01_pytest_fixtures.py -v

---

### Análisis de 01_pytest_fixtures.py

El script valida un diccionario de ruta con `validate_route_payload()` usando
tres fixtures y tres tests.

**Por qué tres fixtures separadas en lugar de crear los dicts dentro del test:**
Cada fixture tiene un nombre descriptivo: `valid_route`, `invalid_route_negative`,
`invalid_route_incomplete`. Al leer el test basta con el nombre para entender qué
escenario se está probando. Si mañana la estructura de una ruta cambia, se actualiza
la fixture una sola vez — no tres tests distintos.

**Por qué los dos `match=` son diferentes:**
`match="Violación de dominio"` verifica el error de valor inválido.
`match="Payload corrupto"` verifica el error de estructura. Son errores distintos
con mensajes distintos — si alguien intercambia las excepciones por error, exactamente
el test equivocado falla, no ambos.

**El flujo del happy path:**
`test_validation_passes_with_correct_data` solo hace `assert ... is True` — no
usa `pytest.raises`. El happy path verifica que la función retorna el valor correcto,
los sad paths verifican que falla con el error correcto.

---

## 3. Mocks con pytest-mock

### Qué problema resuelve un mock

Un test que llama a `httpx.get(url)` de verdad depende de la red, consume cuota de
API, y puede fallar por razones ajenas al código. Un mock reemplaza esa llamada por
un doble controlado que devuelve exactamente lo que el test necesita.

### mocker.patch — la fixture de pytest-mock

`mocker.patch(ruta)` reemplaza el objeto en `ruta` por un `MagicMock` durante el
test. Se revierte automáticamente al finalizar.

```python
def test_fetch_clima_ok(mocker):
    mock_get = mocker.patch("httpx.get")
    mock_get.return_value.json.return_value = {"temp": 22.0, "condition": "Sunny"}
    mock_get.return_value.raise_for_status.return_value = None

    resultado = fetch_clima("Valencia")
    assert resultado["temp"] == 22.0
```

### La regla del path: parchea donde se USA

El path debe apuntar al módulo donde se usa la función, no donde está definida:

```python
# fetch_clima.py importa httpx — el patch va en fetch_clima.httpx.get
mocker.patch("fetch_clima.httpx.get")

# Si parcheas "httpx.get" directamente puede no funcionar:
# el módulo ya tiene su referencia local a httpx.get al importar
```

### side_effect para simular errores

`side_effect` hace que el mock lance una excepción en lugar de retornar un valor:

```python
mock_get.side_effect = httpx.TimeoutException("Read timeout")
# ahora cualquier llamada a mock_get() lanzará TimeoutException
```

---

▶ Ejecuta el ejemplo:
  uv run pytest scripts/clase_04/conceptos/02_pytest_mock.py -v

---

### Análisis de 02_pytest_mock.py

El script tiene un adaptador `get_traffic_status()` que llama a `httpx.get` y
traduce errores de red a errores de dominio. Tres tests cubren sus tres ramas.

**Por qué existe `TrafficAPIError`:**
Es una excepción de dominio — la aplicación no debería exponer `httpx.HTTPStatusError`
hacia arriba. Si mañana se cambia de httpx a requests, el resto de la aplicación
sigue esperando `TrafficAPIError`, no una excepción de httpx. El adaptador traduce
entre el mundo externo y el dominio propio.

**Por qué el test de timeout usa `side_effect` y no `return_value`:**
`side_effect = httpx.TimeoutException(...)` hace que el mock *lance* la excepción
al ser llamado, en lugar de retornar algo. Es la única forma de simular un timeout:
la función no retorna nada, interrumpe la ejecución.

**Qué verifica `assert_called_once_with("https://api.traffic.com/v1/Barcelona", timeout=2.0)`:**
Verifica URL y parámetro `timeout` juntos. Si alguien elimina el `timeout=2.0` de la
llamada real en producción, este test falla inmediatamente. Es un contrato explícito.

**Por qué el test de HTTP 500 usa `match="Fallo en la API de tráfico: HTTP 500"`:**
El mensaje del error incluye el código de estado. Si la función cambia el mensaje
o deja de incluir el código, el test falla. Es una especificación del contrato del
adaptador, no solo una verificación de que algo falló.

---

## 4. @pytest.mark.parametrize

### El antipatrón: loop dentro del test

```python
def test_evaluate_delay_loop():
    casos = [(5, "OK"), (30, "WARNING"), (90, "DANGER")]
    for minutos, esperado in casos:
        assert evaluate_delay(minutos) == esperado  # si falla el 2°, el 3° no se ejecuta
```

Si el caso del medio falla, el test se detiene. No sabes si el tercero también
fallaba. Y el reporte solo muestra un fallo sin decir qué valor lo causó.

### Un case, un test

Con `parametrize`, pytest genera un test independiente por cada caso:

```python
@pytest.mark.parametrize("minutos, esperado", [
    (5,  "OK"),
    (30, "WARNING"),
    (90, "DANGER"),
])
def test_evaluate_delay(minutos: int, esperado: str):
    assert evaluate_delay(minutos) == esperado
```

El reporte muestra `test_evaluate_delay[5-OK]`, `test_evaluate_delay[30-WARNING]`,
`test_evaluate_delay[90-DANGER]` — cada uno independiente. Si el segundo falla,
el tercero sigue ejecutando.

### Edge cases de límite

Los casos más importantes son los que están justo en los límites de cada rama:

```python
@pytest.mark.parametrize("minutos, esperado", [
    (14, "OK"),      # último valor antes del cambio
    (15, "WARNING"), # primer valor de la zona WARNING
    (44, "WARNING"), # último WARNING
    (45, "DANGER"),  # primer DANGER
])
```

Si alguien cambia `< 15` por `<= 15` en el código, exactamente el test `[14-OK]`
y el `[15-WARNING]` fallan — señalando el cambio con precisión.

---

▶ Ejecuta el ejemplo:
  uv run pytest scripts/clase_04/conceptos/03_pytest_parametrize.py -v

---

### Análisis de 03_pytest_parametrize.py

El script define `evaluate_delay(minutes)` con tres zonas (OK/WARNING/DANGER)
y 6 casos parametrizados.

**Por qué 6 casos y no 3:**
Los 3 casos normales (5, 30, 90) verifican el comportamiento esperado en el centro
de cada zona. Los 3 casos de límite (14, 15, 45) verifican los bordes. Es en los
bordes donde las condiciones `< 15` y `< 45` pueden equivocarse.

**Qué dice cada comentario en los casos:**
`# Caso de uso normal`, `# Edge case inferior`, `# Edge case límite` — son
especificaciones, no decoración. Alguien que lee el test 6 meses después entiende
por qué ese número está ahí y qué ocurriría si el código cambiara.

**Por qué el valor 14 y no 13:**
14 es el máximo valor que debe retornar "OK". Si el test usara 10, pasaría tanto
con `< 15` como con `<= 14`. El 14 es específico: solo pasa si la condición es
estrictamente `< 15`.

---

## 5. El Test Integrador

### Combinar los tres patrones

En tests reales, los tres patrones aparecen juntos. Un test que verifica la lógica
de negocio de un orquestador necesita:

- Una **fixture** que defina el estado base del sistema (el usuario, la configuración)
- **Parametrize** para cubrir todas las ramas de la función con distintas entradas
- **mocker** para aislar la dependencia externa

El resultado es un solo test que genera N casos independientes, cada uno con su
propio estado y su propio mock:

```python
@pytest.mark.parametrize("clima, recomendacion", [
    ("Sunny", "Ride a Bike"),
    ("Rain",  "Take the Train"),
])
def test_recomendacion(mocker, perfil_usuario, clima, recomendacion):
    mocker.patch("httpx.get").return_value.json.return_value = {"condition": clima}

    resultado = get_commute_recommendation("Madrid", perfil_usuario)

    assert resultado == recomendacion
```

`perfil_usuario` viene de la fixture. `clima` viene del parametrize. El mock
conecta los dos: inyecta el clima del parametrize en la función bajo test.

---

▶ Ejecuta el ejemplo:
  uv run pytest scripts/clase_04/conceptos/04_commute_integrator.py -v

---

### Análisis de 04_commute_integrator.py

El script combina los tres patrones para verificar `get_commute_recommendation()`,
una función que decide el transporte según el clima y el perfil del usuario.

**Por qué `eco_user_profile` tiene `has_car: False`:**
El perfil del usuario afecta qué rama se ejecuta cuando llueve. Si `has_car` fuera
`True`, el caso `("Rain", "Take the Train")` fallaría — la función tomaría otra rama.
La fixture define explícitamente el escenario que los tests están probando.

**Por qué "Snow" y "Hurricane" van al mismo resultado "Take the Bus":**
Son edge cases del `else` en el código — valores que no están mapeados explícitamente
en el `if/elif`. Verificar que ambos caen en el mismo fallback garantiza que no existe
un `elif "Snow"` escondido. El cuarto caso (`Hurricane`) es el edge case extremo.

**Cómo el parametrize conecta con el mock:**
`clima_simulado` de parametrize se inyecta en `mock_get.return_value.json.return_value`.
Cada ejecución del test tiene un mock distinto configurado con su propio clima. El mock
no sabe qué clima tiene — solo devuelve lo que parametrize le asignó.

**Qué verifica `mock_get.assert_called_once_with("https://api.weather.com/v1/Madrid")`:**
Que la función construyó la URL correctamente con el origen `"Madrid"`. Si alguien
cambia el endpoint en el código, este assert lo detecta aunque el resultado de la
recomendación sea el mismo.
