# Clase 09 — Contratos de Datos con Pydantic V2

## El problema: datos sin garantías

Cuando una función devuelve un `dict`, cualquier clave puede estar ausente,
cualquier valor puede tener el tipo incorrecto, y el error aparece lejos del origen:

```python
# La API devuelve esto
data = {"temperature": 999.0, "description": "hot"}

# ...viaja por el servicio sin error...
# ...llega al historial sin error...
# ...aparece en el output sin error...
# El dato inválido llegó a producción.
```

Pydantic resuelve esto detectando el error **en la frontera** — exactamente donde
el dato externo entra al sistema.

---

## 1. BaseModel — la unidad básica de Pydantic V2

`BaseModel` genera un `__init__` que valida en cada creación:

```python
from pydantic import BaseModel, Field

class Producto(BaseModel):
    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
```

```python
# Creación válida
p = Producto(nombre="Café", precio=2.50)
print(p.nombre)   # "Café"
print(p.stock)    # 0 (default)

# Creación inválida — falla aquí, no después
Producto(nombre="", precio=2.50)
# ValidationError: nombre — String should have at least 1 character
```

**Coerción automática** (lax mode por defecto):
```python
Producto(nombre="Café", precio="2.50")  # "2.50" → 2.50, sin error
```

Pydantic intenta convertir al tipo declarado. Útil cuando los datos vienen de JSON
donde `"24"` y `24` son equivalentes.

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_09/conceptos/01_pydantic_basico.py`

---

## 2. Field — constraints declarativos

`Field` añade validación y documentación al campo:

```python
from pydantic import BaseModel, Field

class Sensor(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)
    valor: float = Field(ge=-100.0, le=100.0)
    unidad: str = Field(pattern=r"^[A-Za-z°%]+$")
    lecturas: list[float] = Field(default_factory=list)
```

### Constraints numéricos

| Constraint | Significado                       |
|-----------|-----------------------------------|
| `gt=0`    | greater than — estrictamente > 0  |
| `ge=0`    | greater or equal — >= 0           |
| `lt=100`  | less than — estrictamente < 100   |
| `le=100`  | less or equal — <= 100            |

### Constraints de string

| Constraint           | Significado                   |
|---------------------|-------------------------------|
| `min_length=1`      | al menos 1 carácter           |
| `max_length=100`    | máximo 100 caracteres         |
| `pattern=r"^\w+$"`  | validación con regex          |

### `default_factory` — defaults mutables

```python
# MAL — mismo bug que def f(x=[])
tags: list[str] = Field(default=[])

# BIEN — cada instancia crea su propia lista
tags: list[str] = Field(default_factory=list)
timestamp: datetime = Field(default_factory=datetime.now)
```

---

## 3. @field_validator — validación custom

Para lógica que `Field` no puede expresar declarativamente:

```python
from pydantic import BaseModel, field_validator

class Temperatura(BaseModel):
    valor: float
    ciudad: str

    @field_validator("valor")
    @classmethod                          # OBLIGATORIO en Pydantic V2
    def rango_realista(cls, v: float) -> float:
        if not -80 <= v <= 60:
            raise ValueError(f"Temperatura imposible: {v}°C")
        return round(v, 1)               # puede transformar el valor

    @field_validator("ciudad")
    @classmethod
    def normalizar(cls, v: str) -> str:
        return v.strip().title()          # "  valencia  " → "Valencia"
```

El `@classmethod` es **obligatorio** en V2. En V1 era opcional — código V1
puede fallar silenciosamente en V2.

### `mode="before"` — antes de la coerción de tipo

```python
@field_validator("fecha", mode="before")
@classmethod
def normalizar_fecha(cls, v):
    if isinstance(v, str):
        return datetime.strptime(v, "%d/%m/%Y")
    return v
```

- `mode="after"` (default): recibe el valor ya convertido al tipo declarado
- `mode="before"`: recibe el valor raw, antes de cualquier conversión

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_09/conceptos/02_field_validators.py`

---

## 4. @model_validator — validación del modelo completo

Cuando la validación necesita acceso a **más de un campo**:

```python
from pydantic import BaseModel, model_validator

class Reserva(BaseModel):
    fecha_entrada: date
    fecha_salida: date
    noches: int | None = None

    @model_validator(mode="after")
    def calcular_noches(self) -> "Reserva":
        if self.fecha_salida <= self.fecha_entrada:
            raise ValueError("La salida debe ser posterior a la entrada")
        self.noches = (self.fecha_salida - self.fecha_entrada).days
        return self
```

```python
r = Reserva(fecha_entrada=date(2024, 6, 1), fecha_salida=date(2024, 6, 5))
print(r.noches)  # 4 — calculado automáticamente
```

`noches` es un **invariante del modelo**: siempre está calculado cuando el objeto
existe. El llamador no puede olvidarlo.

### Orden de ejecución

```
campo 1 → @field_validator("campo1") → ...
campo 2 → @field_validator("campo2") → ...
         ↓
         @model_validator(mode="after")
```

Si un `@field_validator` falla, el `@model_validator` no se ejecuta.

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_09/conceptos/03_model_validator.py`

---

## 5. ValidationError — fallar en la frontera

Cuando la validación falla, Pydantic lanza `ValidationError`:

```python
from pydantic import ValidationError

try:
    Temperatura(valor=999.0, ciudad="Venus")
except ValidationError as e:
    print(e.error_count())      # 1
    for error in e.errors():
        print(error["loc"])     # ('valor',)
        print(error["msg"])     # Value error, Temperatura imposible: 999.0°C
        print(error["type"])    # value_error
```

`ValidationError` agrega **todos los errores** del objeto, no solo el primero:

```python
try:
    Producto(nombre="", precio=-5.0, stock=-1)
except ValidationError as e:
    print(e.error_count())  # 3 — los tres campos fallaron
```

El principio: **el error ocurre exactamente donde el dato inválido intenta
entrar al sistema**, no después cuando ya contaminó otras partes.

---

## 6. model_dump() — serialización

```python
from datetime import datetime

class Pedido(BaseModel):
    id: int
    creado_en: datetime
    items: list[str]

p = Pedido(id=1, creado_en=datetime.now(), items=["café", "pan"])
```

| Método                       | Resultado                        | Notas                           |
|-----------------------------|----------------------------------|---------------------------------|
| `p.model_dump()`            | `dict` Python                    | `datetime` como objeto          |
| `p.model_dump(mode="json")` | `dict` con tipos JSON            | `datetime` como string ISO      |
| `p.model_dump_json()`       | `str` JSON                       | Directo, más rápido             |
| `Pedido.model_validate(d)`  | instancia validada desde `dict`  | Valida al reconstruir           |

```python
# dict Python — datetime como objeto
data = p.model_dump()
print(type(data["creado_en"]))  # <class 'datetime.datetime'>

# dict JSON-compatible — datetime como string
data_json = p.model_dump(mode="json")
print(data_json["creado_en"])   # "2024-03-28T10:30:00"

# reconstruir con validación
p2 = Pedido.model_validate(data)
```

---

## 7. Pydantic vs dataclass vs TypedDict

| Aspecto               | dataclass | TypedDict | Pydantic |
|-----------------------|-----------|-----------|---------|
| Validación runtime    | No        | No        | Sí      |
| Coerción de tipos     | No        | No        | Sí      |
| Serialización JSON    | Manual    | Manual    | Nativa  |
| Overhead              | Mínimo    | Mínimo    | Pequeño |
| Schema JSON           | No        | No        | Sí      |
| Integración FastAPI   | No        | Parcial   | Nativa  |

**Regla de uso:**

- **dataclass** → datos internos, puramente computacionales, sin fronteras del sistema
- **Pydantic** → datos que cruzan una frontera: API externa, base de datos, archivo de configuración, request HTTP
- **TypedDict** → documentar la forma de dicts existentes que no se pueden migrar (código legacy)

```python
# dataclass — datos internos sin validar
@dataclass
class NodoArbol:
    valor: int
    izquierda: "NodoArbol | None" = None
    derecha: "NodoArbol | None" = None

# Pydantic — datos que vienen de una API externa
class RespuestaAPI(BaseModel):
    temperatura: float = Field(ge=-80, le=60)
    ciudad: str = Field(min_length=1)
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_09/conceptos/04_pydantic_vs_dataclass.py`
