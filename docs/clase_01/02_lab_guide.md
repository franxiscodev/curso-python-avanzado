# Lab Guide — Clase 01: El Setup Profesional

> Lee `01_conceptos.md` antes de este lab.
> Aquí construimos directamente sobre esos conceptos — no se re-explican.

## Hito verificable

```bash
uv run python scripts/clase_01/demo_weather.py
```

```
[INFO] PyCommute v0.1.0 iniciado
[INFO] Clima en Valencia: 14°C, clear sky
```

---

## Prerequisitos

- Python 3.12+ instalado
- `uv` instalado
- Cuenta en [openweathermap.org](https://openweathermap.org) con API key gratuita
- Git configurado con tu nombre y email

---

## Parte 1 — Levantar el entorno

> Concepto aplicado: sección 1 de `01_conceptos.md` (UV)

```bash
# Windows (PowerShell) y Linux (idéntico)
git clone <url-del-repo>
cd pycommute
uv sync
```

Verificar que el paquete es importable:

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run python -c "import pycommute; print(pycommute.__version__)"
# Esperado: 0.1.0
```

Si ves `ModuleNotFoundError`, revisa que `uv sync` completó sin errores.

---

## Parte 2 — Configurar la API key

> Concepto aplicado: sección 5 de `01_conceptos.md` (Variables de entorno)

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux
cp .env.example .env
```

Edita `.env` y reemplaza `your_key_here`:

```env
OPENWEATHER_API_KEY=tu_api_key_aqui
```

> `.env` está en `.gitignore`. Nunca hagas commit de este archivo.

---

## Parte 3 — Escribir `weather.py`

> Concepto aplicado: secciones 3 y 4 de `01_conceptos.md` (httpx + Type Hints)

Crea `src/pycommute/weather.py` con la función `get_current_weather`.

**Firma:**

```python
def get_current_weather(city: str, api_key: str) -> dict:
    ...
```

**Contrato:**
- Input: nombre de ciudad y API key
- Output: `dict` con las claves `city`, `temperature`, `description`
- HTTP: usa `httpx.Client` con context manager
- Endpoint: `https://api.openweathermap.org/data/2.5/weather`
- Parámetros: `q=<city>`, `appid=<api_key>`, `units=metric`

**Estructura del JSON de respuesta:**

```json
{
  "name": "Valencia",
  "main": { "temp": 24.12 },
  "weather": [{ "description": "clear sky" }]
}
```

**Checklist antes de continuar:**
- [ ] Type hints en la firma
- [ ] Docstring Google Style en la función
- [ ] `response.raise_for_status()` antes de `.json()`

---

## Parte 4 — Ejecutar el script de demo

> Concepto aplicado: secciones 1, 3 y 5 de `01_conceptos.md` (UV + httpx + .env)

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run python scripts/clase_01/demo_weather.py
```

Output esperado:

```
[INFO] PyCommute v0.1.0 iniciado
[INFO] Clima en Valencia: 14°C, clear sky
```

---

## Parte 5 — Ejecutar los tests

> Concepto aplicado: sección 1 de `01_conceptos.md` (UV — uv run)

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run pytest tests/ -v
```

```
PASSED tests/unit/test_weather.py::test_get_weather_returns_expected_fields
PASSED tests/unit/test_weather.py::test_get_weather_raises_on_bad_key
2 passed
```

---

## Parte 6 — Subir a GitHub

```bash
# Windows (PowerShell) y Linux (idéntico)
git add src/pycommute/weather.py
git commit -m "feat: implementar get_current_weather"
git push origin main
```

---

## Troubleshooting

| Error | Causa probable | Solución |
|-------|---------------|----------|
| `ModuleNotFoundError: pycommute` | `uv sync` no ejecutado | `uv sync` en la raíz del proyecto |
| `httpx.HTTPStatusError: 401` | API key inválida o no activa aún | Revisar `.env`; las keys nuevas tardan ~2 h |
| `httpx.HTTPStatusError: 404` | Ciudad no encontrada | Verificar ortografía |
| `AssertionError: OPENWEATHER_API_KEY no encontrada` | Falta `.env` | `cp .env.example .env` y editar |

---

## ✅ Hito de la Clase 1

Al terminar este lab tu código debe verse como `snapshots/clase_01/`.
Puedes abrirlo para comparar — los comentarios `# [CLASE X →]` explican
qué cambiará en cada punto en las próximas clases.

Ejecuta el comando de verificación:

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run python scripts/clase_01/demo_weather.py
```

Salida esperada:

```
[INFO] PyCommute v0.1.0 iniciado
[INFO] Clima en Valencia: 14°C, clear sky
```
