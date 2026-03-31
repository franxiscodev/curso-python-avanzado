# Conceptos — Clase 02: Structural Pattern Matching

Seis conceptos que transforman cómo navegas estructuras de datos en Python.
Cada sección tiene un ejemplo que puedes copiar y ejecutar por tu cuenta.

---

## 1. ¿Qué es Structural Pattern Matching?

### El problema que resuelve

Cuando recibes un JSON de una API, necesitas inspeccionar su estructura
para decidir qué hacer. Con `if/elif` clásico, el código escala mal:

```python
# Difícil de leer cuando los dicts tienen estructura anidada
if "error" in response:
    handle_error(response["error"])
elif "data" in response and isinstance(response["data"], list):
    process_list(response["data"])
elif "data" in response and isinstance(response["data"], dict):
    process_dict(response["data"])
```

### La solución: `match/case`

Python 3.10 introdujo Structural Pattern Matching (PEP 634). Permite
describir la _forma_ que esperas, y Python hace el matching por ti:

```python
match response:
    case {"error": message}:
        handle_error(message)
    case {"data": [*items]}:
        process_list(items)
    case {"data": dict() as info}:
        process_dict(info)
```

### Breve historia

- **Python 3.9 y antes:** sin `match/case`. Se usaba `if/elif` o diccionarios de dispatch.
- **Python 3.10 (octubre 2021):** PEP 634 introduce `match/case`.
- **PEP 636:** el tutorial oficial de Structural Pattern Matching.

La sintaxis viene inspirada de Rust, Scala y Haskell, donde el pattern matching
es una herramienta fundamental. En Python se adaptó para trabajar de forma
natural con `dict`, `list`, `tuple` y clases.

### Ejemplo mínimo con patrones literales

```python
def describir_codigo_http(codigo: int) -> str:
    match codigo:
        case 200:
            return "OK"
        case 404:
            return "No encontrado"
        case 500:
            return "Error del servidor"
        case _:
            return "Código desconocido"

print(describir_codigo_http(200))   # OK
print(describir_codigo_http(418))   # Código desconocido
```

El `case _:` es el wildcard: captura cualquier valor que no haya coincidido antes.
Equivale al `else` de un `if/elif`.

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_02/conceptos/01_match_case_basico.py`

---

## 2. Patrones básicos

### Literales, variables y wildcard

`match/case` distingue tres tipos de patrones en su forma más básica:

| Patrón | Qué hace | Ejemplo |
|--------|----------|---------|
| Literal | Coincide con un valor exacto | `case 200:` |
| Variable | Captura el valor en una nueva variable | `case codigo:` |
| Wildcard | Captura cualquier cosa, descarta el valor | `case _:` |

### Cómo las variables capturan valores

Cuando usas un nombre que no es una constante en un `case`, Python captura
el valor de la expresión en esa variable:

```python
def clasificar_temperatura(temp: float) -> str:
    match round(temp):
        case 0:
            return "Punto de congelación"
        case valor if valor < 0:
            # 'valor' ahora contiene el valor de round(temp)
            return f"Bajo cero: {valor}°C"
        case valor:
            return f"Temperatura: {valor}°C"

print(clasificar_temperatura(-5.3))   # Bajo cero: -5°C
print(clasificar_temperatura(22.7))   # Temperatura: 23°C
```

### Patrones OR con `|`

Puedes agrupar varios literales en un solo `case` usando `|`:

```python
def categoria_http(codigo: int) -> str:
    match codigo:
        case 200 | 201 | 204:
            return "Éxito"
        case 400 | 401 | 403 | 404:
            return "Error del cliente"
        case 500 | 502 | 503:
            return "Error del servidor"
        case _:
            return "Otro"

print(categoria_http(201))   # Éxito
print(categoria_http(403))   # Error del cliente
```

### Importante: variables vs constantes

Python no puede distinguir por sintaxis si `FOO` es una variable a capturar
o una constante a comparar. La regla es:

- **Nombre simple** (`foo`, `valor`, `x`) → siempre captura, nunca compara.
- **Nombre con punto** (`Status.OK`, `http.HTTPStatus.OK`) → compara contra la constante.

```python
from http import HTTPStatus

def procesar(codigo: int) -> str:
    match codigo:
        case HTTPStatus.OK:          # compara contra la constante 200
            return "OK"
        case otro:                   # captura cualquier otro valor
            return f"Código: {otro}"
```

---

## 3. Patrones de mapping

### Matching sobre diccionarios

Los patrones de mapping permiten hacer match sobre la _estructura_ de un `dict`.
No hace falta listar todas las claves — las claves extra se ignoran por defecto:

```python
def procesar_respuesta(data: dict) -> str:
    match data:
        case {"status": "ok", "value": valor}:
            return f"Valor recibido: {valor}"
        case {"status": "error", "message": msg}:
            return f"Error: {msg}"
        case {"status": estado}:
            return f"Estado desconocido: {estado}"
        case _:
            return "Respuesta no reconocida"

# Las claves extra ("timestamp", "id"...) se ignoran
print(procesar_respuesta({"status": "ok", "value": 42, "timestamp": 1234}))
# Valor recibido: 42

print(procesar_respuesta({"status": "error", "message": "timeout"}))
# Error: timeout
```

### Capturar las claves restantes con `**resto`

Si necesitas las claves que no matchearon, usa `**nombre`:

```python
def inspeccionar(data: dict) -> None:
    match data:
        case {"type": tipo, **resto}:
            print(f"Tipo: {tipo}")
            print(f"Resto del dict: {resto}")

inspeccionar({"type": "sensor", "value": 23.5, "unit": "C"})
# Tipo: sensor
# Resto del dict: {'value': 23.5, 'unit': 'C'}
```

### Verificar tipo del valor con clases

Puedes combinar matching de clave con verificación de tipo:

```python
def validar(data: dict) -> str:
    match data:
        case {"readings": [*_]}:        # 'readings' existe y es una lista
            return "Lecturas en lista"
        case {"readings": dict()}:       # 'readings' existe y es un dict
            return "Lecturas en dict"
        case _:
            return "Estructura no reconocida"
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_02/conceptos/02_match_case_estructuras.py`

---

## 4. Patrones de secuencia

### Matching sobre listas y tuplas

Los patrones de secuencia permiten hacer match sobre la _forma_ de una lista
o tupla: longitud, primeros elementos, resto:

```python
def describir_lista(items: list) -> str:
    match items:
        case []:
            return "Lista vacía"
        case [unico]:
            return f"Un elemento: {unico}"
        case [primero, segundo]:
            return f"Dos elementos: {primero} y {segundo}"
        case [primero, *resto]:
            return f"Empieza por {primero}, luego {len(resto)} elemento(s) más"

print(describir_lista([]))              # Lista vacía
print(describir_lista([42]))            # Un elemento: 42
print(describir_lista([1, 2]))          # Dos elementos: 1 y 2
print(describir_lista([1, 2, 3, 4]))    # Empieza por 1, luego 3 elemento(s) más
```

### El operador `*rest`

`[first, *rest]` captura el primer elemento en `first` y el resto (puede
ser lista vacía) en `rest`. También funciona en el medio: `[first, *middle, last]`.

```python
def analizar_ruta(coordenadas: list) -> str:
    match coordenadas:
        case []:
            return "Sin coordenadas"
        case [unica]:
            return f"Solo un punto: {unica}"
        case [origen, destino]:
            return f"De {origen} a {destino}"
        case [origen, *intermedios, destino]:
            return f"De {origen} a {destino} pasando por {len(intermedios)} punto(s)"

print(analizar_ruta([(0, 0), (1, 1), (2, 2), (3, 3)]))
# De (0, 0) a (3, 3) pasando por 2 punto(s)
```

### Patrones anidados

Los patrones de secuencia y mapping se pueden anidar sin límite:

```python
def procesar_lote(batch: list) -> list[str]:
    resultados = []
    for item in batch:
        match item:
            case {"type": "temperature", "value": float() as v}:
                resultados.append(f"Temp: {v:.1f}°C")
            case {"type": "humidity", "value": int() as v}:
                resultados.append(f"Humedad: {v}%")
            case {"type": tipo, "value": valor}:
                resultados.append(f"{tipo}: {valor}")
            case _:
                resultados.append("Ítem desconocido")
    return resultados

lecturas = [
    {"type": "temperature", "value": 21.5},
    {"type": "humidity", "value": 65},
    {"type": "pressure", "value": 1013},
]
print(procesar_lote(lecturas))
# ['Temp: 21.5°C', 'Humedad: 65%', 'pressure: 1013']
```

---

## 5. Guards

### ¿Qué es un guard?

Un guard es una condición adicional que debe cumplirse para que un `case` coincida.
Se escribe con `if` después del patrón:

```python
case patron if condicion:
    ...
```

El patrón se evalúa primero. Si coincide, Python evalúa la condición.
Solo si ambas son verdaderas se ejecuta el bloque.

### Ejemplo básico

```python
def clasificar_lectura(data: dict) -> str:
    match data:
        case {"sensor": "temperatura", "value": v} if v > 40.0:
            return f"ALERTA: temperatura crítica {v}°C"
        case {"sensor": "temperatura", "value": v} if v < 0.0:
            return f"ALERTA: temperatura bajo cero {v}°C"
        case {"sensor": "temperatura", "value": v}:
            return f"Temperatura normal: {v}°C"
        case {"sensor": tipo}:
            return f"Sensor {tipo}: sin clasificar"

print(clasificar_lectura({"sensor": "temperatura", "value": 45.2}))
# ALERTA: temperatura crítica 45.2°C

print(clasificar_lectura({"sensor": "temperatura", "value": 22.1}))
# Temperatura normal: 22.1°C
```

### Cuándo usar guards

Usa guards cuando la decisión depende del _valor_ de algo capturado, no solo
de su _estructura_. Si la condición solo involucra estructura, es mejor
refinarlo en el patrón directamente.

```python
# Mejor con guard — la condición depende del valor capturado
case {"code": code} if 400 <= code < 500:
    return "error del cliente"

# Mejor sin guard — la estructura es suficiente para distinguirlo
case {"error": message}:
    return f"error: {message}"
```

### Los guards no hacen backtracking

Si el patrón coincide pero el guard falla, Python _no_ prueba el siguiente
`case` con el mismo patrón. Pasa directamente al siguiente `case` completo:

```python
def ejemplo(valor: int) -> str:
    match valor:
        case x if x > 100:
            return "grande"
        case x if x > 50:
            return "mediano"    # solo llega aquí si x <= 100
        case x:
            return f"pequeño: {x}"
```

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_02/conceptos/03_match_case_guards.py`

---

## 6. `match/case` vs `if/elif/else`

### No son equivalentes: cada uno tiene su dominio

La pregunta no es cuál es "mejor" — es cuál es el correcto para cada situación.

### Cuándo `match/case` gana claramente

`match/case` sobresale cuando el flujo depende de la **estructura** del dato:

```python
# Con match/case — la estructura habla por sí sola
def interpretar(respuesta: dict) -> str:
    match respuesta:
        case {"ok": True, "data": {"items": [*elementos]}}:
            return f"{len(elementos)} elemento(s) recibidos"
        case {"ok": False, "error": {"code": codigo, "detail": detalle}}:
            return f"Error {codigo}: {detalle}"
        case {"ok": False, "error": str() as msg}:
            return f"Error: {msg}"
        case _:
            return "Respuesta inesperada"
```

```python
# Con if/elif — el mismo código es más difícil de leer
def interpretar(respuesta: dict) -> str:
    if respuesta.get("ok") is True:
        data = respuesta.get("data", {})
        items = data.get("items", [])
        if isinstance(items, list):
            return f"{len(items)} elemento(s) recibidos"
    elif respuesta.get("ok") is False:
        error = respuesta.get("error", {})
        if isinstance(error, dict):
            return f"Error {error.get('code')}: {error.get('detail')}"
        elif isinstance(error, str):
            return f"Error: {error}"
    return "Respuesta inesperada"
```

### Cuándo `if/elif/else` gana claramente

`if/elif` es más legible cuando las condiciones son **booleanas simples**
y no involucran desestructuración:

```python
# Aquí if/elif es más natural — no hay estructura que descomponer
def puede_procesar(activo: bool, intentos: int, limite: int) -> bool:
    if not activo:
        return False
    elif intentos >= limite:
        return False
    else:
        return True
```

Forzar `match/case` aquí solo añade ruido:

```python
# Antipatrón — match/case usado donde no aporta
match (activo, intentos >= limite):
    case (False, _):
        return False
    case (_, True):
        return False
    case _:
        return True
```

### Tabla de decisión rápida

| Situación | Usar |
|-----------|------|
| Inspeccionar estructura de `dict` o `list` | `match/case` |
| Múltiples variantes de un JSON de API | `match/case` |
| Condiciones booleanas simples | `if/elif/else` |
| Comparar un valor contra rangos numéricos | `if/elif/else` o `match/case` con guards |
| Variantes con estructura diferente cada una | `match/case` |
| Lógica de negocio que no depende de estructura | `if/elif/else` |

▶ Ejecuta el ejemplo:
  `uv run scripts/clase_02/conceptos/04_match_case_vs_if_else.py`
