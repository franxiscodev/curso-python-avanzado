"""Concepto 4 — Contexto estructurado para LLMs.

Demuestra:
- Como construir un prompt a partir de datos tipados (Pydantic models)
- El pipeline completo: WeatherData + RouteData → prompt → JSON → AIRecommendation
- Por que model_dump() es la puerta de entrada al LLM
- Diferencia entre enviar un dict anonimo y datos estructurados

Este script no hace llamadas a la API — muestra el prompt resultante.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_10/conceptos/04_context_to_llm.py

    # Linux
    uv run scripts/clase_10/conceptos/04_context_to_llm.py
"""

import json


# ── Simular datos tipados (como los que devuelven nuestros adaptadores) ──────

def build_travel_prompt(
    origin: str,
    dest: str,
    origin_temp: float,
    origin_desc: str,
    dest_temp: float,
    dest_desc: str,
    routes: list[dict],
) -> str:
    """Construye un prompt con contexto estructurado de viaje.

    En el proyecto real, origin_temp/desc vienen de WeatherData.temperature
    y los routes de list[RouteData]. model_dump() los convierte a dict.
    """
    routes_text = "\n".join([
        f"  - {r['profile']}: {r['distance_km']}km, {r['duration_min']}min"
        for r in routes
    ])

    schema = {
        "recommendation": "recomendacion principal de transporte",
        "suggested_profile": "cycling-regular | driving-car | foot-walking",
        "confidence": "alta | media | baja",
        "reasoning": "razonamiento breve en una linea",
        "outfit_tips": ["item1", "item2"],
        "departure_advice": "consejo de salida",
    }

    return f"""Analiza este viaje:

ORIGEN: {origin} — {origin_temp}°C, {origin_desc}
DESTINO: {dest} — {dest_temp}°C, {dest_desc}

RUTAS:
{routes_text}

Responde UNICAMENTE con JSON:
{json.dumps(schema, ensure_ascii=False, indent=2)}"""


# ── Datos simulados (en el proyecto real vienen de Pydantic models) ──────────

prompt = build_travel_prompt(
    origin="Valencia",
    dest="Madrid",
    origin_temp=13.0,
    origin_desc="nublado",
    dest_temp=5.0,
    dest_desc="nieve ligera",
    routes=[
        {"profile": "driving-car", "distance_km": 350.0, "duration_min": 180.0},
        {"profile": "cycling-regular", "distance_km": 350.0, "duration_min": 1200.0},
        {"profile": "foot-walking", "distance_km": 350.0, "duration_min": 4200.0},
    ],
)

print("Prompt construido:")
print("-" * 60)
print(prompt)
print("-" * 60)
print(f"Longitud: {len(prompt)} caracteres")

# ── El pipeline completo ─────────────────────────────────────────────────────

print()
print("Pipeline completo en GeminiAdapter:")
print()
print("  1. WeatherData (validado por Pydantic)")
print("     → origin_weather.temperature, origin_weather.description")
print()
print("  2. list[RouteData] (validado por Pydantic)")
print("     → [r.profile, r.distance_km, r.duration_min for r in routes]")
print()
print("  3. _build_prompt() — combina todo en texto estructurado")
print()
print("  4. client.aio.models.generate_content(prompt)")
print("     → response.text (JSON como string)")
print()
print("  5. json.loads(clean_json(response.text))")
print("     → dict Python")
print()
print("  6. AIRecommendation(**data) — valida con Pydantic")
print("     → objeto tipado con suggestion, confidence, outfit_tips...")
print()
print("Cada paso tiene un tipo definido.")
print("Si Gemini alucina un perfil invalido, Pydantic lo detecta en el paso 6.")
