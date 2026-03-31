"""Mocks: aislar el sistema bajo test con unittest.mock.

Demuestra el problema que resuelven los mocks (llamadas externas en tests)
y como usar MagicMock para reemplazar dependencias externas.

Ejecutar:
    uv run scripts/clase_04/conceptos/02_pytest_mock.py
"""

from unittest.mock import MagicMock, call

# --- El problema: dependencias externas en tests ---

print("=== Sin mock: el test depende de una conexion real ===")
print()


def obtener_temperatura(url: str) -> float:
    """Simula una llamada HTTP real — falla sin conexion."""
    raise ConnectionError("Sin conexion en este demo")


try:
    temp = obtener_temperatura("https://api.openweathermap.org/...")
except ConnectionError as e:
    print(f"  El test fallaria con: {e}")

print()

# --- MagicMock: reemplazar la dependencia ---

print("=== Con MagicMock: el test no depende de nada externo ===")
print()

# Crear un mock que simula la funcion
mock_obtener = MagicMock(return_value=24.12)

# Llamar al mock como si fuera la funcion real
temperatura = mock_obtener("https://api.openweathermap.org/...")
print(f"  Temperatura obtenida: {temperatura}")

# El mock registra como fue llamado
print(f"  Fue llamado con: {mock_obtener.call_args}")
print(f"  Veces llamado: {mock_obtener.call_count}")

print()

# --- return_value vs side_effect ---

print("=== return_value vs side_effect ===")
print()

# return_value: siempre devuelve el mismo valor
mock_exito = MagicMock(return_value={"temp": 24.12, "desc": "despejado"})
print(f"  return_value: {mock_exito()}")
print(f"  return_value: {mock_exito()}")  # mismo resultado siempre

print()

# side_effect con lista: devuelve cada elemento en orden
mock_secuencia = MagicMock(side_effect=[
    {"temp": 24.12},
    {"temp": 18.5},
    ConnectionError("fallo de red"),
])
print(f"  side_effect[0]: {mock_secuencia()}")
print(f"  side_effect[1]: {mock_secuencia()}")
try:
    mock_secuencia()
except ConnectionError as e:
    print(f"  side_effect[2]: lanza {type(e).__name__}: {e}")

print()

# --- Verificar llamadas al mock ---

print("=== Verificar como fue llamado el mock ===")
print()

mock_cliente = MagicMock()
mock_cliente.get("https://api.ejemplo.com", params={"q": "Valencia"})
mock_cliente.get("https://api.ejemplo.com", params={"q": "Madrid"})

print(f"  call_count: {mock_cliente.get.call_count}")
print(f"  call_args_list:")
for c in mock_cliente.get.call_args_list:
    print(f"    {c}")

# Verificaciones tipicas en tests:
mock_cliente.get.assert_called()              # fue llamado al menos una vez
mock_cliente.get.assert_called_with(          # ultima llamada con estos args
    "https://api.ejemplo.com", params={"q": "Madrid"}
)
print()
print("  assert_called() y assert_called_with() no lanzan error: OK")
