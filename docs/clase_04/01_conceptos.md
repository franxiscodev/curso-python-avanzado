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

En un flujo de integración continua (CI/CD), los tests corren automáticamente en cada
push al repositorio. Si algo se rompe, el pipeline falla antes de que el código llegue
a producción. Esta práctica convierte los tests en una red de seguridad que trabaja
por ti.

### Velocidad: tests con llamadas reales vs mocks

Un test que llama a una API externa puede tardar 2-3 segundos. Si tienes 200 tests así,
tu suite tarda 6-10 minutos. Los mocks (dobles de prueba) reemplazan esas llamadas por
respuestas instantáneas: los mismos 200 tests corren en menos de un segundo.

La regla es simple:
- Tests **unitarios**: sin red, sin disco, sin base de datos. Rápidos y deterministas.
- Tests **de integración**: con dependencias reales. Lentos, pero necesarios para
  verificar que las piezas encajan.

▶ Ejecuta el ejemplo:
  uv run scripts/clase_04/conceptos/01_pytest_basico.py

---

## 2. pytest — estructura básica

### Convenciones de nombres

pytest descubre los tests automáticamente siguiendo estas reglas:

- Los archivos deben llamarse `test_*.py` o `*_test.py`
- Las funciones deben empezar con `test_`
- Las clases (opcionales) deben empezar con `Test`

```python
# test_calculadora.py

def test_suma_dos_enteros():
    assert 2 + 3 == 5

def test_division_entre_cero():
    import pytest
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

### assert nativo — sin self.assertEqual

A diferencia de `unittest`, pytest usa el `assert` nativo de Python. Cuando un assert
falla, pytest reescribe el AST (árbol sintáctico abstracto) de la expresión para
mostrar exactamente qué valor tenía cada lado:

```
AssertionError: assert 4 == 5
  where 4 = suma(2, 2)
```

No necesitas `assertEqual`, `assertIn`, `assertIsNone`... Solo `assert`.

### conftest.py — fixtures compartidas

`conftest.py` es un archivo especial que pytest carga automáticamente. Las fixtures
definidas ahí están disponibles para todos los tests en el mismo directorio y
subdirectorios, sin necesidad de importarlas.

```python
# conftest.py
import pytest

@pytest.fixture
def usuario_ejemplo():
    return {"nombre": "Ana", "edad": 30}
```

```python
# test_usuario.py
def test_nombre_usuario(usuario_ejemplo):
    assert usuario_ejemplo["nombre"] == "Ana"
```

### Ciclo de vida de una fixture: setup → test → teardown

Con `yield`, una fixture puede ejecutar código antes y después del test:

```python
@pytest.fixture
def conexion_temporal():
    # setup: se ejecuta antes del test
    conn = crear_conexion()
    yield conn
    # teardown: se ejecuta siempre, aunque el test falle
    conn.cerrar()
```

### Scope de fixtures

El parámetro `scope` controla cuántas veces se instancia la fixture:

| Scope      | Se ejecuta una vez por... |
|------------|---------------------------|
| `function` | test (default)            |
| `class`    | clase de tests            |
| `module`   | archivo                   |
| `session`  | ejecución completa        |

```python
@pytest.fixture(scope="module")
def cliente_compartido():
    return CrearCliente()
```

▶ Ejecuta el ejemplo:
  uv run scripts/clase_04/conceptos/01_pytest_basico.py

---

## 3. Mocks — aislar el sistema bajo test

### ¿Qué es un mock?

Un mock es un objeto que reemplaza una dependencia externa por un doble controlado.
En lugar de llamar a una API real, abrir un archivo, o consultar una base de datos,
el mock devuelve exactamente lo que tú le indicas.

El objetivo es aislar la unidad que estás probando: quieres verificar **tu código**,
no el comportamiento de servicios externos.

### ¿Cuándo usar mocks?

- Llamadas HTTP a APIs externas
- Consultas a bases de datos
- Operaciones de sistema de archivos
- Funciones que dependen del tiempo (`datetime.now()`)
- Cualquier dependencia que sea lenta, no determinista, o con estado compartido

### MagicMock: return_value y side_effect

`MagicMock` es la clase principal de `unittest.mock`. Acepta cualquier atributo y
llamada sin error, a menos que le indiques lo contrario.

**`return_value`** — lo que retorna cuando se llama a la función:

```python
from unittest.mock import MagicMock

obtener_precio = MagicMock(return_value=42.5)
resultado = obtener_precio("BTC")
assert resultado == 42.5
```

**`side_effect`** — puede ser una excepción, un iterable de valores, o una función:

```python
# Lanzar una excepción
obtener_precio.side_effect = ConnectionError("sin red")

# Retornar valores distintos en llamadas sucesivas
obtener_precio.side_effect = [10.0, 20.0, 30.0]

# Usar una función como reemplazo
obtener_precio.side_effect = lambda simbolo: simbolo.upper()
```

`side_effect` tiene precedencia sobre `return_value`.

### Verificar comportamiento: call_count y assert_called_with

Los mocks registran cómo fueron llamados:

```python
mock_fn = MagicMock(return_value="ok")
mock_fn("hola", clave="valor")

assert mock_fn.call_count == 1
mock_fn.assert_called_once_with("hola", clave="valor")
mock_fn.assert_called_with("hola", clave="valor")  # solo verifica la última llamada
```

Métodos útiles:

| Método | Qué verifica |
|--------|-------------|
| `assert_called_once()` | Se llamó exactamente una vez |
| `assert_called_once_with(...)` | Una vez, con estos argumentos |
| `assert_called_with(...)` | La última llamada tuvo estos argumentos |
| `assert_not_called()` | No se llamó ninguna vez |
| `call_count` | Número total de llamadas |

▶ Ejecuta el ejemplo:
  uv run scripts/clase_04/conceptos/02_mocks.py

---

## 4. pytest-mock — mocker.patch()

### Por qué pytest-mock en lugar de unittest.mock directamente

`unittest.mock` requiere usar `with patch(...)` como context manager o como decorador,
lo que puede hacer los tests más verbosos. `pytest-mock` expone la fixture `mocker`,
que se integra naturalmente con el estilo de pytest y maneja el cleanup automáticamente
al finalizar cada test.

```python
# Con unittest.mock (context manager)
from unittest.mock import patch

def test_con_patch():
    with patch("modulo.funcion") as mock_fn:
        mock_fn.return_value = 99
        assert calcular() == 99
# Al salir del with, el patch se revierte

# Con pytest-mock (fixture)
def test_con_mocker(mocker):
    mock_fn = mocker.patch("modulo.funcion", return_value=99)
    assert calcular() == 99
# Al finalizar el test, pytest-mock revierte automáticamente
```

### El path correcto para patch: dónde se usa, no dónde se define

Esta es la regla más importante —y más confusa— de los mocks:

**Parchea el nombre en el módulo donde se importa y usa, no donde está definido.**

```python
# En requests_helper.py
import httpx

def obtener_datos(url: str) -> dict:
    respuesta = httpx.get(url)  # httpx se usa aquí
    return respuesta.json()
```

```python
# En el test — parchea donde SE USA, no "httpx.get"
def test_obtener_datos(mocker):
    mock_get = mocker.patch("requests_helper.httpx.get")
    mock_get.return_value.json.return_value = {"clave": "valor"}

    resultado = obtener_datos("https://ejemplo.com")
    assert resultado == {"clave": "valor"}
```

Si parcheas `httpx.get` directamente pero `requests_helper` ya importó `httpx`,
el patch no tendrá efecto porque el nombre local ya está enlazado.

### spec= para detectar atributos inexistentes

Por defecto, `MagicMock` acepta cualquier atributo sin error, lo que puede enmascarar
bugs (por ejemplo, llamar a `mock.repsuesta` en lugar de `mock.respuesta`):

```python
from unittest.mock import MagicMock

class Cliente:
    def obtener(self, url: str) -> dict: ...

mock_cliente = MagicMock(spec=Cliente)
mock_cliente.obtener("https://ejemplo.com")  # OK
mock_cliente.obtenerr("https://ejemplo.com")  # AttributeError — typo detectado
```

Con `spec=`, el mock solo acepta atributos y métodos que existen en la clase real.

```python
def test_con_spec(mocker):
    mock = mocker.patch("mi_modulo.Cliente", spec=Cliente)
    mock.return_value.obtener.return_value = {"dato": 1}
    ...
```

▶ Ejecuta el ejemplo:
  uv run scripts/clase_04/conceptos/02_mocks.py

---

## 5. parametrize — un test, múltiples casos

### El antipatrón: loop dentro del test

Un error común al probar múltiples casos es hacer un loop dentro del test:

```python
def test_es_par_loop():
    casos = [2, 4, 6, 8]
    for numero in casos:
        assert numero % 2 == 0  # si falla el caso 3, ¿cuál fue?
```

El problema: si el tercer caso falla, el test se detiene ahí. No sabes si los
siguientes también fallaban. Además, el reporte de pytest muestra un solo fallo
sin indicar qué valor causó el problema.

### @pytest.mark.parametrize — cada caso es un test independiente

Con `parametrize`, pytest genera un test separado por cada caso. Si tres de diez
fallan, ves exactamente cuáles son:

```python
import pytest

@pytest.mark.parametrize("numero", [2, 4, 6, 8])
def test_es_par(numero):
    assert numero % 2 == 0
```

Pytest ejecuta `test_es_par[2]`, `test_es_par[4]`, `test_es_par[6]`, `test_es_par[8]`
como tests independientes.

### Múltiples parámetros

Cuando la función bajo test recibe varios argumentos, los casos se pasan como tuplas:

```python
@pytest.mark.parametrize("a, b, esperado", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, -50, 50),
])
def test_suma(a, b, esperado):
    assert a + b == esperado
```

### IDs personalizados

Por defecto, pytest genera IDs como `test_suma[1-2-3]`. Puedes hacerlos legibles:

```python
@pytest.mark.parametrize("entrada, esperado", [
    ("hola mundo", 2),
    ("una", 1),
    ("", 0),
], ids=["dos_palabras", "una_palabra", "vacia"])
def test_contar_palabras(entrada, esperado):
    assert len(entrada.split()) == esperado
```

Ahora el reporte muestra `test_contar_palabras[dos_palabras]`, que comunica
la intención del caso.

▶ Ejecuta el ejemplo:
  uv run scripts/clase_04/conceptos/03_parametrize.py

---

## 6. monkeypatch — variables de entorno y estado del sistema

### setenv, delenv, setattr

La fixture `monkeypatch` modifica el entorno de ejecución durante un test y revierte
todos los cambios al finalizar:

```python
def test_con_variable_de_entorno(monkeypatch):
    monkeypatch.setenv("API_KEY", "clave-de-prueba")
    # dentro del test, os.environ["API_KEY"] == "clave-de-prueba"
    assert obtener_api_key() == "clave-de-prueba"
    # al salir, la variable vuelve a su estado original

def test_sin_variable_critica(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    # raising=False evita error si la variable no existía
    with pytest.raises(KeyError):
        obtener_configuracion()

def test_con_atributo_modificado(monkeypatch):
    monkeypatch.setattr("os.path.sep", "/")
    assert construir_ruta("a", "b") == "a/b"
```

### Por qué es mejor que modificar os.environ directamente

Si un test hace `os.environ["API_KEY"] = "test"` sin cleanup, esa variable queda
contaminando todos los tests siguientes. El orden de ejecución importa, los tests
no son independientes, y los bugs son difíciles de rastrear.

`monkeypatch` garantiza que cada test parte de un estado limpio, sin importar el orden.

```python
# MAL — contamina el entorno global
def test_malo():
    os.environ["MODO"] = "test"
    assert procesar() == "resultado-test"
    # si este test falla a mitad, la variable queda sucia

# BIEN — cleanup automático garantizado
def test_bien(monkeypatch):
    monkeypatch.setenv("MODO", "test")
    assert procesar() == "resultado-test"
```

### Diferencia entre monkeypatch y mocker

Ambas fixtures modifican el entorno durante el test y revierten al finalizar, pero
tienen propósitos distintos:

| Fixture | Usar para |
|---------|-----------|
| `monkeypatch` | Variables de entorno, atributos simples, paths del sistema |
| `mocker` | Objetos Python, funciones, clases (con tracking de llamadas) |

`monkeypatch` es más simple: modifica un valor y lo restaura. `mocker` crea un
`MagicMock` completo que registra llamadas y permite verificar comportamiento.

Regla práctica: si necesitas verificar cuántas veces se llamó algo o con qué argumentos,
usa `mocker`. Si solo necesitas controlar un valor de entorno o un atributo simple,
usa `monkeypatch`.

▶ Ejecuta el ejemplo:
  uv run scripts/clase_04/conceptos/04_monkeypatch.py
