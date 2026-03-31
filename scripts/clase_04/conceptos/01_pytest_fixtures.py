"""El problema que resuelven las fixtures de pytest.

Demuestra por que el setup repetido en cada test es un problema
y como las fixtures centralizan ese setup.

Ejecutar:
    uv run scripts/clase_04/conceptos/01_pytest_fixtures.py
"""

# --- Sin fixture: setup repetido en cada test ---

print("=== Sin fixture: setup repetido ===")


def preparar_datos_ciudad() -> dict:
    """Setup que se repetiria en cada test sin fixtures."""
    return {"nombre": "Valencia", "temp": 24.12, "descripcion": "cielo despejado"}


def test_sin_fixture_1():
    datos = preparar_datos_ciudad()  # setup repetido
    assert "nombre" in datos
    assert datos["temp"] > 0
    print("  test_sin_fixture_1: OK")


def test_sin_fixture_2():
    datos = preparar_datos_ciudad()  # mismo setup de nuevo
    assert isinstance(datos["temp"], float)
    print("  test_sin_fixture_2: OK")


def test_sin_fixture_3():
    datos = preparar_datos_ciudad()  # y otra vez
    assert datos["nombre"] == "Valencia"
    print("  test_sin_fixture_3: OK")


test_sin_fixture_1()
test_sin_fixture_2()
test_sin_fixture_3()

print()
print("El setup se repite en cada test.")
print("Si el formato de los datos cambia, hay que editar 3 funciones.")
print()

# --- Con fixture: setup centralizado ---

print("=== Con fixture: setup centralizado ===")
print()
print("  # En conftest.py:")
print("  @pytest.fixture")
print("  def datos_ciudad():")
print('      return {"nombre": "Valencia", "temp": 24.12, "descripcion": "cielo despejado"}')
print()
print("  # En test_weather.py (pytest inyecta la fixture automaticamente):")
print("  def test_campos_correctos(datos_ciudad):")
print('      assert "nombre" in datos_ciudad')
print()
print("  def test_temperatura_es_float(datos_ciudad):")
print("      assert isinstance(datos_ciudad['temp'], float)")
print()
print("Si el formato de los datos cambia, solo se edita conftest.py.")
print()

# --- Ciclo de vida de una fixture ---

print("=== Ciclo de vida: setup -> test -> teardown ===")
print()
print("  @pytest.fixture")
print("  def conexion_db():")
print("      conn = abrir_conexion()   # SETUP — se ejecuta antes del test")
print("      yield conn                # el test recibe 'conn' aqui")
print("      conn.close()              # TEARDOWN — se ejecuta despues del test")
print()
print("  def test_query(conexion_db):")
print("      resultado = conexion_db.execute('SELECT 1')")
print("      assert resultado is not None")
print()
print("Ventaja: el teardown se ejecuta incluso si el test falla.")
