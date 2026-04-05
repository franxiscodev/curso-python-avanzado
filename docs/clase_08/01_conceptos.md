# Clase 08 — Conceptos: Arquitectura Hexagonal

## 1. El problema del acoplamiento

Imagina una función que necesita enviar un email:

```python
# Version acoplada — la lógica de negocio y la infraestructura mezcladas
import smtplib

def procesar_pedido(pedido_id: str) -> None:
    # ... lógica del pedido ...
    with smtplib.SMTP("smtp.gmail.com") as servidor:
        servidor.sendmail("origen", "destino", f"Pedido {pedido_id} procesado")
```

Para testear `procesar_pedido` necesitas un servidor SMTP real. Si mañana cambias
a SendGrid, tienes que tocar `procesar_pedido` — que no tiene nada que ver con emails.

**El problema:** la lógica de negocio conoce demasiado sobre la infraestructura.

**Analogía de los enchufes de viaje:** tu laptop (núcleo) no cambia cuando viajas
a UK — solo cambias el adaptador. La Arquitectura Hexagonal hace lo mismo con el software:
el núcleo permanece estable; los adaptadores cambian según el contexto.

La Arquitectura Hexagonal (Alistair Cockburn, 2005) resuelve esto con una regla:

> **El núcleo de la aplicación no depende de la infraestructura.**
> **La infraestructura depende del núcleo.**

```
adapters/weather.py  -->  importa  -->  core/ports.py
adapters/route.py    -->  importa  -->  core/ports.py
services/commute.py  -->  importa  -->  core/ports.py

# NUNCA al revés:
core/ports.py        ✗   NO importa ✗   adapters/weather.py
```

---

## 2. typing.Protocol — duck typing estructural

### typing.Protocol — contratos sin herencia

`Protocol` permite definir contratos de comportamiento. Cualquier clase que
tenga los métodos con la firma correcta satisface el Protocol **sin heredar de él**:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class RoutePort(Protocol):
    async def get_eta_minutes(self, origin: str, destination: str) -> int:
        """Devuelve el tiempo estimado de llegada en minutos."""
        ...
```

### Implementar un Protocol

Las implementaciones concretas no escriben `class Foo(RoutePort)`:

```python
class OpenRouteAdapter:
    async def get_eta_minutes(self, origin: str, destination: str) -> int:
        # llamada real a la API...
        return 45

class GoogleMapsAdapter:
    async def get_eta_minutes(self, origin: str, destination: str) -> int:
        # llamada a otra API...
        return 42

# Ambas satisfacen RoutePort sin herencia — duck typing estructural
```

`@runtime_checkable` habilita `isinstance()` en tiempo de ejecución. Sin él,
`isinstance(obj, RoutePort)` lanzaría `TypeError`. La verificación solo comprueba
que los métodos existen, no sus firmas — para eso está mypy/pyright.

### Función que usa el Protocol

Una función que acepta `RoutePort` funciona con cualquier implementación:

```python
async def calcular_ruta(router: RoutePort, origin: str, dest: str) -> int:
    return await router.get_eta_minutes(origin, dest)

# Funciona con OpenRouteAdapter, GoogleMapsAdapter, o cualquier mock
```

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_08/conceptos/01_protocol_basico.py`

**Qué observar en el script:**
- `RoutePort` define `get_eta_minutes` como `async def` — los adaptadores también deben usar `async def`
- `isinstance(ors_adapter, RoutePort)` devuelve `True` sin herencia alguna
- `OpenRouteAdapter` y `GoogleMapsAdapter` son completamente independientes entre sí
- **Conexión con el proyecto:** `core/ports.py` contiene `WeatherPort`, `RoutePort` y
  `CachePort` con exactamente este patrón. `OpenWeatherAdapter` y `OpenRouteAdapter`
  los implementan sin herencia.

---

## 3. Inyección de dependencias por constructor

La Inyección de Dependencias (DI) resuelve el acoplamiento pasando las
dependencias desde fuera, en lugar de crearlas internamente:

```python
# SIN DI — el servicio crea su propia dependencia (acoplado)
class CommuteService:
    def __init__(self) -> None:
        self._cache = DictCacheAdapter()  # acoplado a una implementación concreta

# CON DI — la dependencia viene de fuera
class CommuteService:
    def __init__(self, cache: CachePort) -> None:
        self._cache = cache  # no sabe qué implementación es
```

**Constructor injection:** las dependencias se pasan al crear el objeto.
Es el patrón más claro — las dependencias son visibles en la firma del `__init__`.

```python
# En producción
service = CommuteService(cache=DictCacheAdapter())

# En tests — sin mocker.patch, sin interceptar módulos
service = CommuteService(cache=FakeCacheAdapter())
```

### Factory como punto de composición

La fábrica (factory) es la función que conoce las implementaciones concretas
y las conecta. El servicio no sabe cuál se eligió:

```python
def crear_servicio(entorno: str) -> CommuteService:
    if entorno == "produccion":
        return CommuteService(cache=DictCacheAdapter())
    elif entorno == "test":
        return CommuteService(cache=FakeCacheAdapter())
    else:
        raise ValueError(f"Entorno desconocido: {entorno}")
```

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_08/conceptos/02_inyeccion_dependencias.py`

**Qué observar en el script:**
- `CachePort` define `get(key)` y `set(key, value)` — interfaz mínima
- `DictCacheAdapter` implementa el contrato con un simple `dict`
- El demo muestra **cache hit**: la segunda llamada con `"ruta_01"` devuelve
  el valor guardado sin recalcular
- **Conexión con el proyecto:** `services/commute.py` recibe `WeatherPort`,
  `RoutePort` y `CachePort` exactamente así. Ningún adaptador se instancia
  dentro del servicio — siempre se inyecta desde fuera.

---

## 4. La regla de dependencia: el Core no conoce el exterior

El script `03_regla_dependencia.py` muestra las tres capas de forma explícita:

```
[CAPA 1 — Core/Dominio]
  WeatherCondition (Pydantic) — el modelo de dominio
  WeatherPort — el contrato que el Core exige
  TripAnalyzer — lógica de negocio pura: sin httpx, sin URLs, sin API keys

[CAPA 2 — Infraestructura/Adaptadores]
  OpenWeatherAdapter — implementa WeatherPort
  Traduce el JSON de la API (temp en Kelvin) al modelo del Core (temp_celsius)

[CAPA 3 — Aplicación]
  Ensambla adaptador + Core y ejecuta
  Es la única capa que conoce ambas partes
```

**Por qué el Core no importa `httpx`:**
Si `TripAnalyzer` importase `httpx`, un cambio en la URL de la API o en la
librería HTTP podría romper la lógica de negocio. Al prohibir esa dirección,
el Core es portable: se testea sin red, sin API keys, sin credenciales.

**La conversión de Kelvin a Celsius es responsabilidad del adaptador:**

```python
# CORRECTO — el adaptador traduce el mundo exterior al modelo del Core
class OpenWeatherAdapter:
    def fetch_weather(self, city: str) -> WeatherCondition:
        api_response = {..., "main": {"temp": 285.15}}  # Kelvin
        temp_c = api_response["main"]["temp"] - 273.15  # adaptador convierte
        return WeatherCondition(temp_celsius=temp_c, is_raining=True)

# INCORRECTO — el Core conoce el formato externo
class TripAnalyzer:
    def should_take_umbrella(self, city: str) -> bool:
        data = self.weather.fetch_weather(city)
        temp_c = data["temp_kelvin"] - 273.15  # el Core no debe saber de Kelvin
```

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_08/conceptos/03_regla_dependencia.py`

**Qué observar en el script:**
- Los comentarios `[CAPA 1/2/3]` marcan la separación de forma explícita
- `TripAnalyzer` no tiene ningún `import` de librería externa
- `OpenWeatherAdapter` hace la conversión Kelvin → Celsius antes de devolver `WeatherCondition`
- **Conexión con el proyecto:** `core/ports.py` y `services/commute.py` son la Capa 1.
  `adapters/weather.py` con `OpenWeatherAdapter` es la Capa 2.
  `demo_proyecto.py` es la Capa 3 — ensambla y ejecuta.

---

## 5. Arquitectura Hexagonal completa

El script `04_hexagonal_completo.py` muestra los cuatro componentes juntos:

```python
# 1. Entidad de dominio — contrato estricto de salida
class CommuteResult(BaseModel):
    origin: str
    destination: str
    ai_recommendation: str
    is_safe: bool

# 2. Puerto — el Core solo conoce este contrato
class AIProviderPort(Protocol):
    def get_advice(self, context: str) -> str: ...

# 3. Servicio — Core que orquesta usando el Puerto
class AdviseService:
    def __init__(self, ai_provider: AIProviderPort) -> None:
        self.ai = ai_provider

    def analyze_route(self, origin: str, dest: str) -> CommuteResult:
        advice = self.ai.get_advice(f"Ruta {origin} -> {dest}")
        return CommuteResult(origin=origin, destination=dest,
                             ai_recommendation=advice,
                             is_safe="peligro" not in advice.lower())

# 4. Adaptadores — intercambiables
class GeminiAdapter:
    def get_advice(self, context: str) -> str:
        return "[Gemini] Salir 10 mins antes"

class OllamaAdapter:
    def get_advice(self, context: str) -> str:
        return "[Gemma local] Ruta despejada"
```

**"Cambiar de Gemini a Ollama es cambiar una línea"** — en el ensamblador:

```python
ai_client = GeminiAdapter()   # produccion
ai_client = OllamaAdapter()   # fallback local — AdviseService no cambia
service = AdviseService(ai_provider=ai_client)
```

`CommuteResult` como Pydantic `BaseModel` garantiza que la salida del servicio
siempre tiene la estructura correcta — no un `dict` libre que puede tener
cualquier forma.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_08/conceptos/04_hexagonal_completo.py`

**Qué observar en el script:**
- `AdviseService` no importa ni `GeminiAdapter` ni `OllamaAdapter` — solo `AIProviderPort`
- El `model_dump_json(indent=2)` muestra la validación Pydantic del resultado
- **Conexión con el proyecto:** en Clase 10 añadimos `GeminiAdapter` real.
  En Clase 11 añadimos `OllamaAdapter` real y `FallbackAIAdapter` que usa ambos.
  Todo esto es posible porque los dos implementan `AIProviderPort` — exactamente
  el patrón de este script.

---

## Resumen: la estructura del proyecto

```
NUCLEO (no conoce el exterior)
  core/ports.py     <- WeatherPort, RoutePort, CachePort (Protocols)
  core/ranking.py   <- lógica de ordenamiento
  core/history.py   <- lógica de historial
  services/commute.py <- CommuteService orquesta usando Ports

      los adaptadores implementan los puertos
              |
              v

ADAPTADORES (implementan los Ports, conocen la infraestructura)
  adapters/weather.py <- OpenWeatherAdapter
  adapters/route.py   <- OpenRouteAdapter
  adapters/cache.py   <- MemoryCacheAdapter
```

**Regla de oro:** `core/` no tiene imports de `adapters/`. `adapters/` importa de `core/`.
