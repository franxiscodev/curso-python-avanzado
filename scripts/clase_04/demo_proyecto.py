"""Demo de la Clase 4 — Testing con pytest.

En la Clase 4 el "demo del proyecto" son los propios tests:
la suite pytest es la evidencia de que el código funciona.
Este script ejecuta los tests y muestra el resultado.

Ejecutar:
    # Windows (PowerShell)
    uv run python scripts/clase_04/demo_proyecto.py

    # Linux
    uv run python scripts/clase_04/demo_proyecto.py
"""

import subprocess
import sys
import time
from pathlib import Path


def run_tests() -> None:
    """Ejecuta pytest y muestra el resultado."""
    print("=== Demo Clase 4 — Testing con pytest ===")
    print()
    print("En testing, el 'demo del proyecto' son los propios tests.")
    print("Una suite verde es la prueba de que el código funciona.")
    print()
    print("Ejecutando: pytest tests/ -v")
    print("-" * 60)

    repo_root = Path(__file__).parent.parent.parent.parent
    curso_root = repo_root / "curso"

    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=curso_root,
        capture_output=False,
    )
    elapsed = time.perf_counter() - start

    print("-" * 60)
    print()

    if result.returncode == 0:
        print(f"Todos los tests pasaron en {elapsed:.2f}s.")
        print()
        print("Lo que cubre esta suite:")
        print("  - Fixtures: datos de prueba reutilizables sin llamadas a API")
        print("  - parametrize: un test, múltiples casos de entrada")
        print("  - mocker: reemplaza llamadas HTTP reales con respuestas simuladas")
        print("  - pytest.raises: verifica que las excepciones se lanzan correctamente")
    else:
        print(f"Algunos tests fallaron (código de salida: {result.returncode}).")
        print("Revisa el output de arriba para ver cuáles.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    run_tests()
