"""parametrize: un test, multiples casos de prueba.

Demuestra por que un loop en el test es un antipatron y como
@pytest.mark.parametrize convierte cada caso en un test independiente.

Ejecutar:
    uv run scripts/clase_04/conceptos/03_pytest_parametrize.py
"""

# --- La funcion que vamos a testear ---


def clasificar_temperatura(temp: float) -> str:
    """Clasifica la temperatura en una categoria descriptiva."""
    if temp < 0:
        return "bajo cero"
    if temp < 15:
        return "frio"
    if temp < 25:
        return "templado"
    return "calido"


# --- Antipatron: loop en el test ---

print("=== Antipatron: loop en el test ===")
print()

casos = [(-5, "bajo cero"), (10, "frio"), (22, "templado"), (30, "calido")]

errores = 0
for temp, esperado in casos:
    resultado = clasificar_temperatura(temp)
    if resultado == esperado:
        print(f"  OK  {temp:4}deg -> {resultado}")
    else:
        print(f"  FAIL {temp:4}deg -> esperado={esperado}, obtenido={resultado}")
        errores += 1

print()
if errores == 0:
    print("Todos los casos pasaron.")
else:
    print(f"{errores} casos fallaron.")

print()
print("Problema: si el caso de -5deg falla, el loop se detiene")
print("y no sabes cuantos otros casos tambien fallan.")
print()

# --- Patron correcto: parametrize ---

print("=== Patron correcto con @pytest.mark.parametrize ===")
print()
print("  @pytest.mark.parametrize('temp,esperado', [")
print("      (-5,  'bajo cero'),")
print("      (10,  'frio'),")
print("      (22,  'templado'),")
print("      (30,  'calido'),")
print("  ])")
print("  def test_clasificar_temperatura(temp, esperado):")
print("      assert clasificar_temperatura(temp) == esperado")
print()
print("Con parametrize, pytest ejecuta 4 tests independientes:")
print("  test_clasificar_temperatura[-5-bajo cero]")
print("  test_clasificar_temperatura[10-frio]")
print("  test_clasificar_temperatura[22-templado]")
print("  test_clasificar_temperatura[30-calido]")
print()
print("Si [-5-bajo cero] falla, los otros 3 se siguen ejecutando.")
print("El reporte muestra exactamente que caso fallo y con que valores.")
print()

# --- Parametrize con multiples parametros ---

print("=== Parametrize con multiples parametros ===")
print()
print("  @pytest.mark.parametrize('ciudad,pais,esperado', [")
print("      ('Valencia', 'ES', True),")
print("      ('Paris',    'FR', True),")
print("      ('',         'ES', False),")
print("  ])")
print("  def test_ciudad_valida(ciudad, pais, esperado):")
print("      assert es_ciudad_valida(ciudad, pais) == esperado")
print()

# --- Parametrize con IDs personalizados ---

print("=== IDs personalizados para mejor legibilidad ===")
print()
print("  @pytest.mark.parametrize('temp,esperado', [")
print("      (-5,  'bajo cero'),")
print("      (10,  'frio'),")
print("  ], ids=['bajo_cero', 'frio'])")
print()
print("Genera: test_clasificar[bajo_cero] y test_clasificar[frio]")
print("(mas legible que test_clasificar[-5-bajo cero])")
