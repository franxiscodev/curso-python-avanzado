# Clase 02 — Parsing Moderno: Structural Pattern Matching

---

## 1. ¿Qué es Structural Pattern Matching?

Python 3.10 introdujo `match/case` (PEP 634). No es un `switch/case` como en C o Java
—que solo compara valores escalares. Es **deconstrucción estructural**: el intérprete
verifica la forma del dato y extrae subvalores en un solo paso.

```python
def interpretar_respuesta(payload: dict) -> str:
    match payload:
        case {"status": "ok", "data": {"items": [*elementos]}}:
            return f"{len(elementos)} elemento(s) recibidos"
        case {"status": "error", "mensaje": str(msg)}:
            return f"Error: {msg}"
        case _:
            return "Respuesta inesperada"
```

Esto sería imposible con un `switch` clásico — necesita `if/elif` con `.get()` y
`isinstance()`. Con `match/case`, la estructura del dato esperado está explícita en
el patrón mismo.

### Los tipos de patrones que usaremos

| Patrón | Ejemplo | Qué hace |
|--------|---------|----------|
| **Literal** | `case "EXITO":` | Coincide con un valor exacto |
| **OR** | `case "A" \| "B":` | Agrupa varias alternativas en un `case` |
| **Wildcard** | `case _:` | Captura cualquier valor sin vincularlo |
| **Mapping** | `case {"key": var}:` | Descompone un dict y captura valores |
| **Secuencia** | `case [primero, *resto]:` | Descompone una lista |
| **Guard** | `case {"v": v} if v > 100:` | Condición adicional sobre variable capturada |
| **Clase** | `case Tren(linea=l):` | Descompone una instancia de dataclass |

### Patrones de clase — dataclasses

Con dataclasses, `match/case` puede descomponer instancias por nombre de campo:

```python
from dataclasses import dataclass

@dataclass
class Sensor:
    tipo: str
    valor: float

def procesar(s: Sensor) -> str:
    match s:
        case Sensor(tipo="temperatura", valor=v) if v > 40:
            return f"Alerta: {v}°C"
        case Sensor(tipo="temperatura", valor=v):
            return f"Normal: {v}°C"
        case Sensor(tipo=t):
            return f"Sensor de {t}"
```

Esto es el mismo mecanismo que los mapping patterns, aplicado a atributos de instancia.

### La regla de los nombres en patrones

En `match/case`, **un nombre simple siempre captura — nunca compara**:

```python
estado = "pendiente"

match valor:
    case estado:      # CAPTURA — vincula valor a la variable estado (sobreescribe)
        ...
```

Para comparar contra una variable existente, usar un guard:

```python
match valor:
    case v if v == estado:   # COMPARA — guard sobre variable capturada
        ...
```

---

## 2. match/case básico — literales, OR y wildcard

### Literales, normalización y OR

El caso más sencillo: `match/case` sobre strings. Cada `case` compara contra
literales. El OR (`|`) agrupa varias alternativas en un solo `case`:

```python
def estado_pedido(estado: str) -> str:
    match estado.upper():
        case "COMPLETADO":
            return "Pedido entregado."
        case "EN_CAMINO" | "PREPARANDO":
            return "Pedido en proceso."
        case "CANCELADO":
            return "Pedido cancelado."
        case _:
            return f"Estado no reconocido: {estado}"
```

`estado.upper()` normaliza antes del match — un solo paso que cubre todas las
variaciones de capitalización. El `case _:` (wildcard) captura todo lo que no
coincidió antes; equivale al `else` de `if/elif`.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_02/conceptos/01_match_case_basico.py

---

### Análisis de 01_match_case_basico.py

`procesar_estado_pago()` recibe tres estados: `"exito"`, `"Procesando"` y
`"REEMBOLSADO"`.

**Por qué `.upper()` antes del `match`:**
Sin normalización, habría que duplicar los cases para cada variante de
capitalización (`"exito"`, `"Exito"`, `"EXITO"`...). Normalizar una vez
antes del match mantiene los patrones limpios.

**Por qué `"PENDIENTE" | "PROCESANDO"` comparten case:**
Ambos estados representan el mismo significado de negocio: el pago está en la
cola. Un solo mensaje de respuesta cubre ambos sin repetir código.

**Por qué `"REEMBOLSADO"` llega al wildcard:**
No está en ningún `case` explícito. El wildcard captura cualquier valor
no mapeado y devuelve un mensaje genérico en lugar de fallar silenciosamente.

---

## 3. Patrones de mapping y secuencia

### Descomponer dicts con patrones de mapping

Los patrones de mapping verifican que ciertas claves existen en el dict y
capturan sus valores. Las claves extra se ignoran — el patrón es **parcial**
por defecto:

```python
def procesar_evento(evento: dict) -> str:
    match evento:
        case {"tipo": "alerta", "nivel": nivel, "origen": origen}:
            return f"Alerta nivel {nivel} desde {origen}"
        case {"tipo": "info", "mensaje": msg}:
            return f"Info: {msg}"
        case {"tipo": tipo}:
            return f"Evento desconocido: {tipo}"
        case _:
            return "Payload sin tipo."
```

Un dict con claves `"tipo"`, `"nivel"`, `"origen"` y `"timestamp"` coincidirá
con el primer `case` aunque tenga `"timestamp"` — las claves extra no rompen
el patrón.

### Secuencias dentro de mappings

Los patrones de secuencia y mapping se anidan. `[primer_archivo, *_]` dentro
de un mapping pattern captura el primer elemento de la lista e ignora el resto:

```python
case {"evento": "commit", "archivos": [primero, *_]}:
    # primero = primer archivo del commit
    # *_ = el resto, ignorado
```

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_02/conceptos/02_match_case_estructuras.py

---

### Análisis de 02_match_case_estructuras.py

`parsear_webhook()` procesa tres payloads de un sistema tipo GitHub.

**Por qué `[primer_archivo, *_]` y no solo `archivos`:**
El `*_` captura el resto de la lista y lo descarta. Con solo `"archivos": archivos`
se capturaría la lista completa — aquí solo se necesita el primer elemento.
Es más preciso en cuanto a la intención.

**Por qué el tercer case usa `{"evento": evento_desconocido}` sin más claves:**
Este patrón actúa como fallback parcial: el dict tiene clave `"evento"` pero
no es "commit" ni "issue". El valor se captura en `evento_desconocido` para
incluirlo en el mensaje.

**Por qué el cuarto `case _:` es necesario:**
Si llega un dict completamente vacío `{}`, ningún patrón anterior coincide
porque todos exigen la clave `"evento"`. El wildcard final captura ese caso.

---

## 4. Guards: condiciones sobre valores capturados

### Qué es un guard y cuándo usarlo

Un guard es una condición `if` que se añade después del patrón. El patrón
se evalúa primero; si coincide, se evalúa el guard. Solo si ambos son
verdaderos se ejecuta el bloque:

```python
case {"temp": t} if t > 40:
    return "temperatura crítica"
```

La diferencia con `if/elif`: el patrón extrae el valor (`t`) y el guard
lo evalúa en la misma expresión. Con `if/elif` habría que acceder al valor
dos veces: primero para extraerlo, luego para compararlo.

Usar guards cuando la decisión depende del **valor** de algo capturado.
Si la diferencia es solo de **estructura**, usar un patrón más específico.

### El orden de los cases con guards

Si el guard falla, Python no abandona el `match` — continúa con el
siguiente `case`. Esto significa que los cases más específicos (con guards
más restrictivos) deben ir primero:

```python
case {"usuario": u, "total": total} if total > 1000:   # más restrictivo
    return f"Alerta de fraude: {u}"
case {"usuario": u, "total": total}:                    # más general
    return f"Compra aprobada: {u}"
```

Si el orden se invirtiera, el segundo case capturaría todas las compras
incluso las fraudulentas, y el primero nunca ejecutaría.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_02/conceptos/03_match_case_guards.py

---

### Análisis de 03_match_case_guards.py

`procesar_compra()` recibe tres carritos: compra de alto valor (fraude),
carrito vacío y compra normal.

**Por qué el guard `if total > 1000` va en el primer case:**
Si estuviera en el tercero, el segundo case (`case {"usuario": u, "total": total}`)
capturaría primero todas las compras normales, y el guard del fraude nunca
evaluaría. El orden de evaluación top-down es crítico.

**Por qué `"items": []` no necesita guard:**
El patrón `[]` ya especifica exactamente que la lista debe estar vacía —
es una condición estructural, no de valor. El guard es para condiciones
que no se pueden expresar en el patrón (rangos numéricos, comparaciones).

**Qué ocurre con Alice (total 1500):**
El primer case coincide: el dict tiene `"usuario"` y `"total"`, y el guard
`total > 1000` es True. Devuelve la alerta de fraude.
Con Bob (total 0, items vacío): el segundo case coincide antes que el tercero.

---

## 5. match/case vs if/elif

### No son equivalentes: cada uno tiene su dominio

La regla práctica:
- **`match/case`** cuando el código bifurca según la **estructura** del dato
- **`if/elif`** cuando el código bifurca según **condiciones booleanas simples**

### El mismo problema, dos soluciones

El script compara las dos versiones sobre el mismo dict con tres niveles de
profundidad:

```python
mensaje = {
    "tipo": "mensaje_texto",
    "contenido": "Hola equipo",
    "metadata": {"urgencia": "alta"}
}
```

La versión imperativa necesita tres `if` anidados para llegar al campo
`"metadata"/"urgencia"`. La versión declarativa lo expresa como un único
patrón de mapping anidado.

```python
# Declarativo — la estructura esperada es visible en el patrón
case {"tipo": "mensaje_texto", "contenido": msg, "metadata": {"urgencia": "alta"}}:
    return f"[URGENTE] Dice: {msg}"
```

Ambas versiones producen el mismo resultado. La diferencia es de legibilidad
y mantenibilidad.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_02/conceptos/04_match_case_vs_if_else.py

---

### Análisis de 04_match_case_vs_if_else.py

`parse_imperativo()` y `parse_declarativo()` reciben el mismo `mensaje` y
devuelven el mismo resultado.

**Por qué la versión imperativa necesita tres niveles de `if`:**
Cada nivel accede a una clave: primero `"tipo"`, luego `"contenido"`, luego
`data["metadata"]["urgencia"]`. Sin verificar explícitamente si cada clave
existe, cualquier acceso puede lanzar `KeyError`. La versión imperativa tiene
que proteger cada nivel.

**Por qué la versión declarativa no necesita `if` anidados:**
El patrón `{"metadata": {"urgencia": "alta"}}` ya verifica en un solo paso
que `"metadata"` existe, que tiene clave `"urgencia"`, y que su valor es
`"alta"`. Si cualquiera de esas condiciones falla, el patrón no coincide y
se pasa al siguiente `case`.

**Cuándo `if/elif` es mejor:**
Si la función recibiera `activo: bool` e `intentos: int` sin diccionarios,
`if/elif` sería más legible. `match/case` añade valor cuando hay estructuras
a descomponer — no para comparaciones simples de escalares.
