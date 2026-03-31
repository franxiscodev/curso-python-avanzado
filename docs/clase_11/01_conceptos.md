# Conceptos Clase 11 — IA Local y Fallback

## 1. Ollama — IA local sin internet

Ollama es un servidor que corre modelos de lenguaje en tu máquina local.
No requiere internet ni API key una vez instalado.

### Cómo funciona

```
Tu código  →  ollama SDK  →  localhost:11434  →  modelo en RAM  →  respuesta
```

Ollama descarga los modelos en formato GGUF (comprimido) y los carga en RAM.
Una vez cargado, el modelo procesa requests sin conexión externa.

### Instalar y usar

```bash
# Instalar Ollama
# Windows: descargar desde https://ollama.com/download
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# Descargar un modelo
ollama pull gemma3:1b    # 815 MB — recomendado para VMs con 4 GB

# Verificar que está corriendo
ollama list
ollama serve             # si no está como servicio del sistema
```

### Por qué es útil

- Sin dependencia de internet — funciona offline
- Sin costo por token — procesar 1 millón de tokens es gratis
- Sin límite de cuota — sin 429 RESOURCE_EXHAUSTED
- Privacidad — los datos no salen de tu máquina

▶ Ejecuta el ejemplo:
```bash
uv run scripts/clase_11/conceptos/01_ollama_basico.py
```

---

## 2. ollama SDK Python — AsyncClient

El SDK `ollama` es una envoltura sobre la API REST local de Ollama.

### Chat básico

```python
import ollama

client = ollama.AsyncClient()  # async — compatible con anyio

response = await client.chat(
    model="gemma3:1b",
    messages=[
        {"role": "system", "content": "Asistente de movilidad"},
        {"role": "user", "content": "¿Qué ropa llevar si llueve?"},
    ],
)

texto = response.message.content
```

### AsyncClient vs Client

```python
# En código async — SIEMPRE usar AsyncClient
client = ollama.AsyncClient()
response = await client.chat(...)

# Client síncrono — NO usar con anyio/asyncio
client = ollama.Client()
response = client.chat(...)  # bloquea el event loop
```

### Manejo de errores

```python
try:
    response = await client.chat(model="gemma3:1b", messages=[...])
except ollama.ResponseError as e:
    print(f"Modelo no encontrado: {e.error}")
    # Solución: ollama pull gemma3:1b
except Exception as e:
    print(f"Ollama no está corriendo: {e}")
    # Solución: ollama serve
```

▶ Ejecuta el ejemplo:
```bash
uv run scripts/clase_11/conceptos/02_ollama_structured.py
```

---

## 3. El patrón Fallback

El patrón Fallback resuelve la pregunta:
**¿Qué hace el sistema cuando el servicio principal falla?**

### Motivación

Sin fallback:
```python
# Si Gemini falla → excepción → el usuario no recibe nada
result = await gemini.get_recommendation(...)
```

Con fallback:
```python
try:
    result = await gemini.get_recommendation(...)
except Exception:
    result = await ollama.get_recommendation(...)  # siempre disponible
```

### El Composite pattern

El truco es encapsular el fallback en su propio adaptador:

```python
class FallbackAI:
    def __init__(self, primary, secondary) -> None:
        self._primary = primary
        self._secondary = secondary

    async def get_recommendation(self, ...) -> AIRecommendation:
        try:
            return await self._primary.get_recommendation(...)
        except Exception as e:
            logger.warning(f"Primario falló: {e} — usando secundario")
            return await self._secondary.get_recommendation(...)
```

`FallbackAI` implementa la misma interfaz — el consumidor no sabe que hay fallback.

### ¿Por qué el fallback no va en el consumidor?

```python
# Sin Composite — el consumidor conoce dos implementaciones concretas
class CommuteService:
    async def get_commute_info(self, ...):
        try:
            rec = await self._gemini.get_recommendation(...)
        except Exception:
            rec = await self._ollama.get_recommendation(...)

# Con Composite — el consumidor conoce solo el puerto
class CommuteService:
    async def get_commute_info(self, ...):
        rec = await self._ai.get_recommendation(...)  # no sabe cuál
```

Con el Composite, añadir un tercer proveedor solo modifica `FallbackAI` —
`CommuteService` no se toca.

▶ Ejecuta el ejemplo:
```bash
uv run scripts/clase_11/conceptos/03_patron_fallback.py
```

---

## 4. Circuit Breaker vs Fallback simple

El Fallback simple que implementamos tiene un límite:
**siempre paga el costo de intentar el primario**.

### Fallback simple

```
Request 1: intenta Gemini → falla (2s) → usa Ollama
Request 2: intenta Gemini → falla (2s) → usa Ollama
Request 3: intenta Gemini → falla (2s) → usa Ollama
```

Si Gemini está caído durante horas, cada request paga 2 segundos extra.

### Circuit Breaker

```
5 fallos consecutivos → OPEN (circuito abierto)
Estado OPEN: bypass directo a Ollama (sin intentar Gemini)
Cada 60s → HALF-OPEN: prueba una request a Gemini
Éxito → CLOSED (vuelve a intentar Gemini normalmente)
```

### ¿Cuándo usar cada uno?

| Situación | Recomendación |
|-----------|--------------|
| Fallos esporádicos (cuota diaria) | Fallback simple |
| Servicio caído por horas | Circuit Breaker |
| Alto volumen (>100 req/min) | Circuit Breaker |
| Prototipo / curso | Fallback simple |

Para PyCommute usamos Fallback simple — los fallos son esporádicos
y el volumen es bajo.

▶ Ejecuta el ejemplo:
```bash
uv run scripts/clase_11/conceptos/04_resiliencia_comparativa.py
```

---

## 5. Principio de Sustitución de Liskov

**LSP (Liskov Substitution Principle):**
> Cualquier objeto de tipo `S` debe poder sustituir a un objeto de tipo `T`
> sin que el comportamiento del programa cambie.

### Con Protocol en Python

```python
from typing import Protocol

class AIPort(Protocol):
    async def get_recommendation(self, ...) -> AIRecommendation: ...

# Todos cumplen AIPort — son sustituibles
servicio = CommuteService(ai=GeminiAdapter(...))    # OK
servicio = CommuteService(ai=OllamaAdapter(...))    # OK
servicio = CommuteService(ai=FallbackAIAdapter(...)) # OK
```

El `CommuteService` no sabe — ni le importa — cuál está usando.

### LSP va más allá de la firma

No basta con tener los mismos métodos. Los contratos implícitos también importan:

```python
# Viola LSP aunque tenga la firma correcta:
class RotoAdapter:
    async def get_recommendation(self, ...) -> AIRecommendation:
        raise NotImplementedError("siempre falla")  # ← rompe el programa
```

Un adaptador que cumple LSP:
- Devuelve un `AIRecommendation` válido, O
- Propaga una excepción recuperable (que el llamador puede manejar)
- No introduce contratos nuevos que el llamador no espera

### La conexión con Clase 8

En Clase 8 definimos `AIPort` como `Protocol`.
Esa decisión hace posible que Gemini, Ollama y FallbackAI sean intercambiables hoy.
**El diseño de hace tres clases pagó dividendos ahora.**
