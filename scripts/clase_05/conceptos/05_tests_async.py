"""Testing async con pytest-anyio y AsyncMock.

Demuestra tres patrones de testing async:
1. Por qué los tests síncronos no funcionan con coroutines
2. @pytest.mark.anyio: ejecutar tests async con event loop real
3. AsyncMock: reemplazar una coroutine por un mock controlado

Cada patron escribe un test en un archivo temporal y ejecuta pytest
via subprocess para mostrar el output real al alumno.

Ejecutar:
    uv run python scripts/clase_05/conceptos/05_tests_async.py
"""

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from loguru import logger


def _run_pytest(test_content: str) -> None:
    """Escribe test en directorio temporal, ejecuta pytest y muestra output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # El plugin anyio debe registrarse explícitamente cuando no hay
        # conftest.py del proyecto en el path.
        (tmp / "conftest.py").write_text('pytest_plugins = ("anyio",)\n', encoding="utf-8")
        (tmp / "test_demo.py").write_text(test_content, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(tmp / "test_demo.py"), "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(result.stderr)


# ---------------------------------------------------------------------------
# Sección 1 — El problema: test síncrono con función async
# ---------------------------------------------------------------------------

logger.info("=" * 60)
logger.info("Sección 1 — El problema: test síncrono con función async")
logger.info("=" * 60)

print("""
Cuando llamas a una función async sin 'await', no obtienes su resultado:
obtienes un objeto coroutine que no se ha ejecutado todavía.

Un test síncrono que haga esto:

    def test_mi_funcion_asincrona():
        resultado = mi_funcion_async()   # <coroutine object> — NO ejecuta nada
        assert resultado == "esperado"   # SIEMPRE falla

...nunca llega a comparar el valor real. Python emite:
    RuntimeWarning: coroutine 'mi_funcion_async' was never awaited

La solución: el test necesita un event loop que ejecute la coroutine.
pytest-anyio lo gestiona automáticamente con @pytest.mark.anyio.
""")

# ---------------------------------------------------------------------------
# Sección 2 — Solución: @pytest.mark.anyio
# ---------------------------------------------------------------------------

logger.info("=" * 60)
logger.info("Sección 2 — Solución: @pytest.mark.anyio")
logger.info("=" * 60)

_test_anyio = textwrap.dedent("""\
    import pytest
    import anyio


    async def sumar_con_delay(a: int, b: int) -> int:
        # Simula I/O asíncrono: cede el control al event loop
        await anyio.sleep(0)
        return a + b


    @pytest.mark.anyio
    async def test_suma_basica():
        # pytest-anyio crea un event loop, ejecuta la coroutine y lo cierra
        resultado = await sumar_con_delay(2, 3)
        assert resultado == 5


    @pytest.mark.anyio
    async def test_suma_grande():
        resultado = await sumar_con_delay(100, 200)
        assert resultado == 300
""")

print("Test:")
print(_test_anyio)
print("Output de pytest:")
_run_pytest(_test_anyio)

# ---------------------------------------------------------------------------
# Sección 3 — AsyncMock: mockear una coroutine
# ---------------------------------------------------------------------------

logger.info("=" * 60)
logger.info("Sección 3 — AsyncMock: mockear una coroutine")
logger.info("=" * 60)

_test_mock = textwrap.dedent("""\
    import pytest
    from unittest.mock import AsyncMock


    # Función de producción que queremos aislar en el test
    async def fetch_datos(url: str) -> dict:
        raise NotImplementedError("No llamar en tests — reemplazar con mock")


    # Orquestador: esto es lo que realmente testamos
    async def procesar(url: str) -> str:
        datos = await fetch_datos(url)
        return datos["resultado"]


    @pytest.mark.anyio
    async def test_procesar_con_mock(monkeypatch):
        # AsyncMock: cuando se 'await'-ea, devuelve el return_value
        mock_fetch = AsyncMock(return_value={"resultado": "ok"})
        monkeypatch.setattr("test_demo.fetch_datos", mock_fetch)

        resultado = await procesar("https://api.ejemplo.com/datos")

        assert resultado == "ok"
        # assert_awaited_once_with: verifica que se llamó con los args exactos
        mock_fetch.assert_awaited_once_with("https://api.ejemplo.com/datos")
""")

print("Test:")
print(_test_mock)
print("Output de pytest:")
_run_pytest(_test_mock)

logger.success("Demo completada.")
