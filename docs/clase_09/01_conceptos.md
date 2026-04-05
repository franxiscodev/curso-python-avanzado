# Conceptos — Clase 09: Contratos de Datos con Pydantic V2

Cuando `fetch_clima` devuelve un `dict`, el código no sabe si
`data["temperature"]` es un `float`, un `str` o `None` hasta que lo usa.
El error aparece lejos del origen y sin contexto.

Pydantic resuelve esto declarando el contrato en el tipo:

```python
class LecturaClima(BaseModel):
    temperatura: float = Field(ge=-80, le=60)
    ciudad: str = Field(min_length=1)
```

Si `temperatura` llega como `"22.5"` (string), Pydantic la convierte.
Si llega como `999.0`, lanza `ValidationError` en ese momento exacto — no
diez funciones después.

---

## 1. BaseModel y coerción de tipos

`BaseModel` genera un `__init__` que valida y convierte cada campo al tipo
declarado. Este comportamiento se llama **coerción** (lax mode por defecto).

```python
from pydantic import BaseModel

class LecturaClima(BaseModel):
    temperatura: float
    ciudad: str
    activo: bool
```

```python
# Los datos de una API JSON llegan como strings
lectura = LecturaClima(temperatura="22.5", ciudad="Valencia", activo="true")

print(lectura.temperatura)  # 22.5 — float, no string
print(lectura.activo)       # True — bool, no string
```

Cuando la conversión no es posible, Pydantic lanza `ValidationError` con
el detalle de cada campo que falló — todos a la vez, no uno por uno:

```python
from pydantic import ValidationError

try:
    LecturaClima(temperatura="muy_caliente", ciudad="Valencia", activo="quizas")
except ValidationError as e:
    print(e.error_count())   # 2 — los dos campos fallaron
    for err in e.errors():
        print(err["loc"], err["msg"])
```

### Field — constraints declarativos

`Field` añade restricciones que Pydantic comprueba tras la coerción:

```python
from pydantic import BaseModel, Field

class LecturaClimaValidada(BaseModel):
    temperatura: float = Field(ge=-80, le=60)
    humedad:     int   = Field(ge=0, le=100)
    ciudad:      str   = Field(min_length=1)
```

| Constraint | Significado |
|-----------|-------------|
| `gt=0`    | estrictamente mayor que 0 |
| `ge=0`    | mayor o igual que 0 |
| `lt=100`  | estrictamente menor que 100 |
| `le=100`  | menor o igual que 100 |
| `min_length=1` | al menos 1 carácter |
| `max_length=50` | máximo 50 caracteres |

### Field con alias — mapeo de nombres externos

Cuando la API externa usa nombres distintos a los campos Python del modelo:

```python
from pydantic import BaseModel, ConfigDict, Field

class EstacionMeteo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    station_id:   str   = Field(alias="id")
    station_name: str   = Field(alias="name")
    elevation_m:  float = Field(alias="elevation")
```

Con `populate_by_name=True`, el modelo acepta tanto el alias como el nombre
Python al construir la instancia:

```python
# Por alias (como llega del JSON de la API)
e1 = EstacionMeteo(id="ES001", name="Valencia Norte", elevation=12.5)

# Por nombre Python (útil en tests y código interno)
e2 = EstacionMeteo(station_id="ES001", station_name="Valencia Norte", elevation_m=12.5)
```

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_09/conceptos/01_pydantic_coercion.py`

### Analiza la salida

El script usa `Dispositivo` con `id: int` y `esta_activo: bool`. Los datos
de entrada son strings (`"101"`, `"true"`).

- **Caso A**: Pydantic convierte los strings a los tipos declarados. Los
  `assert` verifican que `dispositivo.id` es el entero `101`, no el string.
  El `logger.success` confirma la coerción.

- **Caso B**: `"no_soy_un_numero"` no tiene conversión válida a `int`.
  `"tal vez"` no tiene conversión válida a `bool`. El `ValidationError`
  muestra **ambos errores a la vez** — Pydantic no para en el primero.
  Cada error incluye: campo, valor recibido, motivo del fallo.

---

## 2. @field_validator — reglas de negocio por campo

Para lógica que `Field` no puede expresar declarativamente (rangos físicos,
transformaciones de formato, checks contra base de datos):

```python
from pydantic import BaseModel, field_validator

class SensorTemperatura(BaseModel):
    lectura: float

    @field_validator("lectura")
    @classmethod                           # OBLIGATORIO en Pydantic V2
    def validar_cero_absoluto(cls, v: float) -> float:
        if v < -273.15:
            raise ValueError("Temperatura por debajo del cero absoluto")
        return v                           # siempre devolver el valor
```

El `@classmethod` es **obligatorio** en V2 — en V1 era opcional y el código
antiguo puede fallar silenciosamente al migrar.

### mode="before" vs mode="after"

```python
# mode="after" (default) — recibe el valor ya convertido al tipo declarado
@field_validator("lectura")
@classmethod
def check_rango(cls, v: float) -> float:   # v ya es float
    ...

# mode="before" — recibe el valor raw, antes de la coerción de tipo
@field_validator("ciudad", mode="before")
@classmethod
def normalizar(cls, v) -> str:             # v puede ser cualquier cosa
    if isinstance(v, str):
        return v.strip().title()
    return v
```

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_09/conceptos/02_field_validators.py`

### Analiza la salida

El script usa `SensorTemperatura` con un validador que aplica la ley
física del cero absoluto (-273.15 °C).

- **Caso A** (`lectura=25.5`): el validador imprime la lectura en curso
  y la deja pasar — es una temperatura físicamente posible.
- **Caso B** (`lectura=-300.0`): `-300 < -273.15`, el validador lanza
  `ValueError`. Pydantic lo captura y lo convierte en `ValidationError`
  indicando exactamente qué campo falló y con qué valor.
- El `print(f"  Validando lectura: {v}")` hace visible que el validador
  se ejecuta una vez por instancia, no en el body del `__init__`.

---

## 3. @model_validator — validación entre múltiples campos

`@field_validator` solo ve un campo a la vez. Cuando la regla involucra
la **relación entre dos o más campos**, se usa `@model_validator`:

```python
from pydantic import BaseModel, model_validator

class FiltroRuta(BaseModel):
    distancia_min: float
    distancia_max: float

    @model_validator(mode="after")
    def verificar_rango(self) -> "FiltroRuta":
        if self.distancia_max <= self.distancia_min:
            raise ValueError("distancia_max debe ser mayor que distancia_min")
        return self          # siempre devolver self
```

### Orden de ejecución

```
campo 1 → @field_validator("campo1") → ...
campo 2 → @field_validator("campo2") → ...
                        ↓
          @model_validator(mode="after")
```

Si un `@field_validator` falla, el `@model_validator` no se ejecuta.
El objeto nunca llega a existir con datos inconsistentes.

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_09/conceptos/03_model_validator.py`

### Analiza la salida

El script usa `RangoFechas` con campos `inicio` y `fin` como enteros
`AAAAMMDD`. Ningún `@field_validator` podría comparar los dos campos.

- **Caso A** (`inicio=20240101`, `fin=20241231`): el print de debug confirma
  que el model_validator recibe ambos valores ya convertidos a `int`. El rango
  es lógico — la instancia se crea.
- **Caso B** (`inicio=20241231`, `fin=20240101`): fin < inicio, la regla
  cross-field lo detecta. El `ValidationError` muestra el error sin indicar
  un campo específico — el error es del modelo completo, no de un campo.

---

## 4. Serialización — model_dump y aliases de salida

Una vez validado el dato, Pydantic permite exportarlo con control total
sobre qué campos salen y con qué nombres:

```python
class ResultadoRuta(BaseModel):
    duracion_min: int
    distancia_km: float
    perfil: str
    _cache_key: str = Field(exclude=True)   # nunca sale en el dump
```

| Método | Resultado | Caso de uso |
|--------|-----------|-------------|
| `model_dump()` | `dict` Python | ORM, librería interna |
| `model_dump(by_alias=True)` | `dict` con alias | API externa |
| `model_dump_json()` | `str` JSON | respuesta HTTP directa |
| `model_validate(d)` | instancia validada | reconstruir desde dict |

### serialization_alias — nombre distinto en la salida

Cuando la API que consumes espera claves diferentes a los nombres Python:

```python
class LecturaClima(BaseModel):
    temperatura: float = Field(..., serialization_alias="temp_c")
    descripcion: str

lectura = LecturaClima(temperatura=22.5, descripcion="soleado")
print(lectura.model_dump())                   # {"temperatura": 22.5, "descripcion": "soleado"}
print(lectura.model_dump(by_alias=True))      # {"temp_c": 22.5, "descripcion": "soleado"}
```

▶ Ejecuta el ejemplo:
  `uv run python scripts/clase_09/conceptos/04_pydantic_serializacion.py`

### Analiza la salida

El script usa `UsuarioAPI` con tres campos notables:
- `email` tiene `serialization_alias="user_email"`
- `token_interno` tiene `exclude=True`

**Escenario A** (`model_dump()` estándar): el dict contiene `email` con
su nombre Python. `token_interno` no aparece — `Field(exclude=True)` lo
elimina en todos los dumps sin excepción.

**Escenario B** (`model_dump(by_alias=True)`): `email` desaparece del dict
y aparece como `user_email`. `by_alias=True` activa todos los
`serialization_alias` del modelo a la vez.

**Escenario C** (`model_dump_json(...)`): genera un string JSON directamente,
más eficiente que `json.dumps(model_dump(...))`. La exclusión ad-hoc
`exclude={"id"}` elimina campos adicionales sin modificar el modelo.

---

## 5. Pydantic vs dataclass vs TypedDict

| Aspecto | dataclass | TypedDict | Pydantic |
|---------|-----------|-----------|---------|
| Validación en runtime | No | No | Sí |
| Coerción de tipos | No | No | Sí |
| Serialización JSON | Manual | Manual | Nativa |
| Overhead | Mínimo | Mínimo | Pequeño |
| Schema JSON | No | No | `model_json_schema()` |
| Integración FastAPI | No | Parcial | Nativa |

**Cuándo usar cada uno:**

- **Pydantic** — datos que cruzan una frontera del sistema: respuesta de API,
  configuración de entorno, request HTTP, datos de base de datos. Cualquier
  dato que venga de fuera del proceso Python.
- **dataclass** — datos puramente internos y computacionales. `NodoArbol`,
  `Coordenada`, estructuras auxiliares que nunca salen del proceso.
- **TypedDict** — documentar la forma de dicts existentes que no se pueden
  migrar (código legacy, librerías que devuelven dicts sin más).

```python
# dataclass — nodo interno del algoritmo de Dijkstra
@dataclass
class NodoRuta:
    ciudad: str
    distancia_acumulada: float
    anterior: "NodoRuta | None" = None

# Pydantic — respuesta de fetch_clima que viene de OpenWeather
class LecturaClima(BaseModel):
    temperatura: float = Field(ge=-80, le=60)
    ciudad: str = Field(min_length=1)
```
