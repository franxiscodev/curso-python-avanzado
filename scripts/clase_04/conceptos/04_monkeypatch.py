"""monkeypatch: controlar el entorno en tests.

Demuestra como manipular variables de entorno para tests
y por que monkeypatch es superior a modificar os.environ directamente.

Ejecutar:
    uv run scripts/clase_04/conceptos/04_monkeypatch.py
"""

import os

# --- La funcion que depende del entorno ---


def get_config() -> dict:
    """Lee configuracion desde variables de entorno.

    Returns:
        Diccionario con la configuracion leida del entorno.

    Raises:
        ValueError: Si API_KEY no esta configurada.
    """
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise ValueError("API_KEY no configurada")
    return {
        "api_key": api_key,
        "entorno": os.environ.get("APP_ENV", "development"),
    }


# --- Sin monkeypatch: modificar os.environ directamente ---

print("=== Sin monkeypatch: riesgo de contaminar el entorno ===")
print()

original_env = os.environ.copy()

try:
    os.environ["API_KEY"] = "test-key-123"
    os.environ["APP_ENV"] = "testing"

    config = get_config()
    print(f"  Config cargada: {config}")
    assert config["api_key"] == "test-key-123"
    print("  Verificacion OK")
    print()

    # Si el test falla aqui, el entorno queda contaminado
    del os.environ["API_KEY"]
    try:
        get_config()
    except ValueError as e:
        print(f"  ValueError esperado: {e}")

finally:
    # Hay que restaurar manualmente — si se olvida, afecta otros tests
    os.environ.clear()
    os.environ.update(original_env)
    print()
    print("  Entorno restaurado manualmente (riesgo: olvidarlo en un test real)")

print()

# --- Con monkeypatch: pytest restaura automaticamente ---

print("=== Con monkeypatch: restauracion automatica ===")
print()
print("  def test_config_carga_env(monkeypatch):")
print('      monkeypatch.setenv("API_KEY", "test-key-123")')
print('      monkeypatch.setenv("APP_ENV", "testing")')
print()
print("      config = get_config()")
print('      assert config["api_key"] == "test-key-123"')
print()
print("  # Al finalizar el test, monkeypatch restaura las variables automaticamente.")
print("  # Aunque el test lance una excepcion, la limpieza ocurre igual.")
print()

print("=== Operaciones disponibles en monkeypatch ===")
print()
print("  monkeypatch.setenv('VAR', 'valor')    # setea una variable")
print("  monkeypatch.delenv('VAR')              # elimina una variable")
print("  monkeypatch.setattr(obj, 'attr', val) # reemplaza un atributo")
print("  monkeypatch.syspath_prepend('/ruta')  # modifica sys.path")
print()
print("Regla de uso:")
print("  monkeypatch -> para estado del entorno (env vars, atributos, paths)")
print("  mocker      -> para reemplazar objetos y funciones (httpx.Client, etc.)")
