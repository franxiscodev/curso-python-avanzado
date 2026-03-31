# Lab Guide — Clase 02: Pattern Matching sobre JSONs de APIs

> Lee `01_conceptos.md` antes de este lab.
> Aquí construimos directamente sobre esos conceptos — no se re-explican.

## ¿Por qué construimos esto así?

En esta clase introducimos OpenRouteService junto con OpenWeather
en lugar de esperar. El JSON de rutas tiene más variantes estructurales
que el de clima — distintos perfiles, errores distintos, listas anidadas —
lo que hace que `match/case` tenga más valor demostrativo trabajando con ambos.

Creamos `route.py` como módulo separado (no extendemos `weather.py`)
porque cada módulo tiene una responsabilidad: `weather.py` sabe de clima,
`route.py` sabe de rutas. En la Clase 8 cada uno se convertirá en un adaptador
de la arquitectura hexagonal — la separación ya estará hecha.

---

## Hito verificable

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run python scripts/clase_02/demo_proyecto.py
```

```
[INFO] PyCommute v0.1.0 iniciado
[INFO] Clima en Valencia: 14°C, clear sky
[INFO] Ruta encontrada: 3.2 km, 12 min en bicicleta
[INFO] Ruta encontrada: 5.1 km, 8 min en coche
```

---

## Prerequisitos

- Lab de la Clase 1 completado (`weather.py` funcionando)
- Cuenta en [openrouteservice.org](https://openrouteservice.org) con API key gratuita (plan público)
- `.env` ya configurado con `OPENWEATHER_API_KEY`

---

## Parte 1 — Agregar la API key de OpenRouteService

Edita `.env` y añade la clave nueva junto a la existente:

```env
OPENWEATHER_API_KEY=tu_key_openweather
OPENROUTESERVICE_API_KEY=tu_key_openrouteservice
```

> `.env.example` ya incluye `OPENROUTESERVICE_API_KEY=your_key_here` como referencia.
> Nunca hagas commit de `.env`.

---

## Parte 2 — Refactorizar `weather.py` con `match/case`

> Concepto aplicado: sección 3 de `01_conceptos.md` (Patrones de mapping)

Abre `src/pycommute/weather.py`. Localiza el bloque donde extraes los campos
del JSON de respuesta con `dict.get()` y reemplázalo por `match/case`.

**Antes (con `dict.get`):**

```python
city = data.get("name", "")
temperature = data.get("main", {}).get("temp", 0.0)
description = data.get("weather", [{}])[0].get("description", "")
```

**Después (con `match/case`):**

```python
match data:
    case {
        "name": str() as city,
        "main": {"temp": float() | int() as temperature},
        "weather": [{"description": str() as description}, *_],
    }:
        return {
            "city": city,
            "temperature": round(float(temperature), 1),
            "description": description,
        }
    case {"message": str() as msg}:
        raise ValueError(f"API respondió con error: {msg}")
    case _:
        raise ValueError(f"Respuesta inesperada de OpenWeather: {data}")
```

**Checklist antes de continuar:**
- [ ] Los tests existentes de `test_weather.py` siguen pasando sin cambios
- [ ] La función devuelve el mismo contrato que antes (`city`, `temperature`, `description`)

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run pytest tests/unit/test_weather.py -v
```

---

## Parte 3 — Crear `route.py`

> Concepto aplicado: secciones 3 y 4 de `01_conceptos.md` (Patrones de mapping y secuencia)

Crea el archivo `src/pycommute/route.py`.

**Firma de la función:**

```python
def get_route(
    origin: tuple[float, float],
    destination: tuple[float, float],
    profile: str,
    api_key: str,
) -> dict[str, Any]:
    ...
```

**Contrato:**
- Input: `origin` y `destination` en formato `(lat, lon)` — ORS usa `[lon, lat]`, hay que invertir
- Input: `profile` es el perfil de transporte que acepta ORS (e.g. `"cycling-regular"`, `"driving-car"`)
- Output: `dict` con las claves `distance_km`, `duration_min`, `profile`
- HTTP: usa `httpx.Client` con context manager
- Endpoint: `https://api.openrouteservice.org/v2/directions/{profile}`
- La key va en el header `Authorization` (no en query params)

**Estructura del JSON de respuesta de ORS (caso exitoso):**

```json
{
  "routes": [
    {
      "summary": {
        "distance": 3215.4,
        "duration": 741.0
      }
    }
  ]
}
```

La distancia viene en metros y la duración en segundos — convierte a km y minutos.

**Ejemplo de implementación del parsing con `match/case`:**

```python
match data:
    case {"routes": [{"summary": {"distance": float() | int() as dist_m,
                                   "duration": float() | int() as dur_s}}, *_]}:
        return {
            "distance_km": round(dist_m / 1000, 2),
            "duration_min": round(dur_s / 60, 1),
            "profile": profile,
        }
    case {"error": {"message": str() as msg}}:
        raise ValueError(f"ORS error: {msg}")
    case _:
        raise ValueError(f"Respuesta inesperada de ORS: {data}")
```

**Checklist antes de continuar:**
- [ ] Type hints completos en la firma
- [ ] Docstring Google Style en la función
- [ ] `response.raise_for_status()` antes de `.json()`
- [ ] La inversión `(lat, lon)` → `[lon, lat]` está hecha correctamente

---

## Parte 4 — Agregar fixture de rutas

> Concepto aplicado: sección 4 de `01_conceptos.md` (Patrones de secuencia — se ven en los tests)

Crea el archivo `tests/fixtures/route_valencia.json` con una respuesta real
(o representativa) de ORS para una ruta corta. Estructura mínima:

```json
{
  "routes": [
    {
      "summary": {
        "distance": 3200.0,
        "duration": 720.0
      }
    }
  ]
}
```

Este archivo lo usarás como mock en los tests para no depender de la red.

---

## Parte 5 — Crear `test_route.py`

Crea `tests/unit/test_route.py` con dos tests básicos:

**Test 1 — campos de retorno correctos:**

```python
def test_get_route_returns_expected_fields(monkeypatch, ...):
    # Mockea httpx para devolver route_valencia.json
    # Verifica que el resultado tiene "distance_km", "duration_min", "profile"
```

**Test 2 — conversión de unidades:**

```python
def test_get_route_converts_units_correctly(monkeypatch, ...):
    # Con distance=3200.0 m y duration=720.0 s
    # Verifica distance_km == 3.2 y duration_min == 12.0
```

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run pytest tests/unit/test_route.py -v
```

```
PASSED tests/unit/test_route.py::test_get_route_returns_expected_fields
PASSED tests/unit/test_route.py::test_get_route_converts_units_correctly
2 passed
```

---

## Parte 6 — Verificar el hito con el script de demo

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run python scripts/clase_02/demo_proyecto.py
```

El script llama a `get_current_weather` y a `get_route` con dos perfiles distintos,
mostrando los resultados con `print()` (aún no tenemos `loguru` — eso es Clase 3).

---

## Troubleshooting

| Error | Causa probable | Solución |
|-------|---------------|----------|
| `httpx.HTTPStatusError: 401` | API key de ORS inválida o ausente | Verificar `OPENROUTESERVICE_API_KEY` en `.env` |
| `ValueError: Respuesta inesperada de ORS` | Perfil de ruta incorrecto | Usar `"cycling-regular"` o `"driving-car"` |
| `KeyError: 'routes'` | Match no cubrió el caso de error de ORS | Revisar el `case {"error": ...}` |
| Tests de `weather.py` fallan tras refactorizar | El contrato de retorno cambió | Verificar que devuelves `city`, `temperature`, `description` |

---

## ✅ Hito de la Clase 2

Tu código al terminar debe verse como `snapshots/clase_02/`.
Puedes abrirlo para comparar — los comentarios `# [CLASE X]` explican
qué se introdujo en cada punto y qué cambiará en clases posteriores.

```bash
# Windows (PowerShell) y Linux (idéntico)
uv run python scripts/clase_02/demo_proyecto.py
```

Salida esperada:

```
[INFO] PyCommute v0.1.0 iniciado
[INFO] Clima en Valencia: 14°C, clear sky
[INFO] Ruta encontrada: 3.2 km, 12 min en bicicleta
[INFO] Ruta encontrada: 5.1 km, 8 min en coche
```
