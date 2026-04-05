# Clase 03 — Resiliencia Profesional: Loguru, Pydantic-Settings y Tenacity

---

## 1. ¿Por qué observabilidad y resiliencia?

Un servicio que funciona en local puede fallar de formas silenciosas en producción:
una API key faltante que retorna `None`, un timeout de red que no se reintenta, un
error que el operador nunca ve porque se perdió entre `print()` genéricos.

Esta clase introduce tres herramientas que atacan cada uno de esos puntos:

- **Loguru**: reemplaza `print()` y el módulo estándar `logging` con output
  estructurado, filtrable y orientado a múltiples destinos.
- **Pydantic-Settings**: lee y valida la configuración al arrancar — si falta una
  variable de entorno requerida, el servicio no arranca y el error es inmediato.
- **Tenacity**: añade reintentos automáticos ante fallos de red transitorios,
  sin código de bucle manual.

Juntas forman el escudo de cualquier servicio que llama a APIs externas.

---

## 2. Loguru — niveles y sinks múltiples

### Cómo funciona loguru

Loguru tiene un único logger global. Por defecto escribe a `stderr` sin filtro.
En producción, lo habitual es reemplazar ese comportamiento con dos destinos:
uno para el operador (solo mensajes importantes) y otro para auditoría (todo).

```python
import sys
from loguru import logger

logger.remove()                                          # elimina el sink por defecto
logger.add(sys.stderr, level="INFO", colorize=True)     # operadores: INFO+
logger.add("auditoria.log", level="DEBUG", rotation="1 MB")  # registro completo
```

`logger.remove()` sin argumentos elimina todos los sinks registrados.
`logger.add()` puede recibir un stream, una ruta de archivo, o cualquier callable.
El parámetro `rotation="1 MB"` rota el archivo cuando supera 1 MB — sin código
adicional de gestión de archivos.

### Niveles de log

| Nivel      | Cuándo usarlo                                            |
|------------|----------------------------------------------------------|
| `DEBUG`    | Estado interno durante desarrollo — nunca en consola de producción |
| `INFO`     | Eventos normales del flujo — lo que el operador debe ver |
| `WARNING`  | Situación inesperada pero recuperable                   |
| `ERROR`    | Fallo en una operación específica                       |
| `CRITICAL` | Fallo que impide continuar la ejecución                 |

La regla práctica: el sink de consola para el operador va en `"INFO"`. El sink de
archivo para el equipo técnico va en `"DEBUG"`. Un mismo mensaje puede llegar a
ambos o solo a uno según el nivel configurado en cada sink.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_03/conceptos/01_loguru_basico.py

---

### Análisis de 01_loguru_basico.py

El script configura dos sinks y llama a `procesar_datos()` con tres niveles distintos.

**Por qué `logger.remove()` antes de `logger.add()`:**
Sin `remove()`, el sink por defecto sigue activo. Si después se añade otro hacia
`sys.stderr`, el mismo mensaje aparecería dos veces. Eliminar primero garantiza
que solo hay los sinks que el código define explícitamente.

**Por qué el DEBUG no aparece en consola:**
El sink de `sys.stderr` tiene `level="INFO"`. El mensaje `logger.debug(...)` tiene
severidad menor — el sink lo descarta. Sí llega al archivo porque su nivel es
`"DEBUG"`. Dos sinks, dos contratos de filtrado distintos.

**Qué ocurre con `rotation="1 MB"`:**
Cuando `sistema_auditoria.log` alcanza 1 MB, loguru lo renombra automáticamente
con timestamp y crea uno nuevo. El archivo siempre existe y nunca crece sin límite.

---

## 3. Loguru — evaluación perezosa y contexto con bind()

### Evaluación perezosa: por qué importa en logs de debug

El problema con f-strings en logs:

```python
def generar_reporte_pesado() -> str:
    # operación costosa de CPU o I/O
    return "Reporte PDF Generado"

# Con f-string: la función se ejecuta ANTES de que loguru filtre el nivel
logger.debug(f"Datos: {generar_reporte_pesado()}")  # la función corre siempre

# Con lambda: la función solo se ejecuta si DEBUG está activo
logger.debug("Datos: {}", lambda: generar_reporte_pesado())
```

Si el sink está en `WARNING`, el mensaje `DEBUG` se descartará. Con f-string,
`generar_reporte_pesado()` ya corrió — trabajo en vano. Con lambda, loguru
evalúa el valor solo cuando sabe que el mensaje va a emitirse.

### Contexto con bind()

`logger.bind()` devuelve un sub-logger con campos extra fijos. Cada mensaje
emitido por ese sub-logger incluye esos campos automáticamente:

```python
user_logger = logger.bind(user_id="usr_99X", ip="192.168.1.5")
user_logger.warning("Intento de login fallido.")   # incluye user_id e ip
user_logger.warning("Contraseña restablecida.")    # incluye user_id e ip
```

El logger original no se modifica. `bind()` devuelve una copia con el contexto
añadido — útil para rastrear todos los eventos de un mismo usuario o request.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_03/conceptos/02_loguru_formato.py

---

### Análisis de 02_loguru_formato.py

**Por qué `generar_reporte_pesado()` nunca se ejecuta:**
El script configura el sink en `"WARNING"`. El nivel `DEBUG` está por debajo —
el mensaje se descarta. Al usar `lambda: generar_reporte_pesado()`, loguru no
invoca la lambda porque sabe que el mensaje no va a emitirse. La función nunca corre.
El `print("--- ⚠️ ATENCIÓN")` dentro nunca aparece en el output.

**Qué se ve en el output de bind():**
Las dos líneas de `user_logger.warning(...)` muestran el mensaje con los campos
`user_id` y `ip` añadidos. Cambiar el nivel del sink a `"DEBUG"` mostraría también
el resultado de la lazy eval — útil para verificar el comportamiento en local.

**Por qué `# Incorrecto` está comentado:**
La línea `logger.debug(f"Datos: {generar_reporte_pesado()}")` está comentada
intencionalmente. Si se descomenta, la función correría — y el `print` de advertencia
aparecería — aunque el mensaje de log nunca llegue al sink. El contraste con la
línea de lambda es el punto central del script.

---

## 4. Pydantic-Settings — configuración tipada y fail-fast

### El problema del None silencioso

```python
import os

api_key = os.getenv("OPENWEATHER_API_KEY")   # None si no está en el entorno
response = client.get(url, headers={"Authorization": f"Bearer {api_key}"})
# El servidor recibe: "Bearer None" — responde 401
# El error aparece al hacer la llamada, no al arrancar
```

`os.getenv()` devuelve `None` sin ninguna advertencia. El error se descubre
tarde, cuando el servicio ya está en producción procesando peticiones reales.

### Pydantic-Settings como solución

```python
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    puerto: int          # lee PUERTO del entorno, convierte a int
    debug: bool          # lee DEBUG del entorno, convierte a bool
    api_key: str         # requerido — sin default, sin None posible

config = AppConfig()     # ValidationError aquí si falta api_key
```

Al instanciar `AppConfig()`, pydantic-settings:
1. Lee las variables de entorno correspondientes
2. Convierte los strings del entorno al tipo declarado (`"8080"` → `8080`)
3. Lanza `ValidationError` inmediatamente si un campo requerido no existe

El servicio no puede arrancar en estado inválido.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_03/conceptos/03_pydantic_settings.py

---

### Análisis de 03_pydantic_settings.py

**Por qué `PUERTO="8080"` (string) se convierte a `int` sin código extra:**
Pydantic lee el tipo declarado (`puerto: int`) y aplica coerción automática.
`"8080"` se convierte a `8080`. `"True"` se convierte a `True`. No hay
`int(os.getenv("PUERTO"))` manual — pydantic lo hace al instanciar.

**Por qué el script falla intencionalmente:**
`API_KEY_SECRETA` no está en `os.environ`. Como el campo no tiene valor
por defecto, pydantic lanza `ValidationError` con el mensaje:
`api_key_secreta: Field required`. El `try/except` captura ese error y
lo imprime como `[FAIL-FAST ACTIVO]`. El servidor no arranca.

**La diferencia con os.getenv():**
Con `os.getenv("API_KEY_SECRETA")` la función retornaría `None` silenciosamente.
Con pydantic-settings el proceso termina con un mensaje de error claro, en el
momento de arranque, antes de procesar ninguna petición real.

---

## 5. Tenacity — @retry declarativo

### El problema del bucle manual

```python
# Sin tenacity — frágil y verboso
intentos = 0
while intentos < 3:
    try:
        resultado = llamar_api(url)
        break
    except ConnectionError:
        intentos += 1
        time.sleep(2 ** intentos)
if intentos == 3:
    raise ConnectionError("API no disponible")
```

Este código mezcla la lógica de negocio con la lógica de retry. Si la función
tiene múltiples puntos de fallo, el bucle se vuelve inmantenible.

### Tenacity: declarar el comportamiento, no el bucle

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def llamar_api(url: str) -> dict:
    response = httpx.get(url, timeout=5.0)
    response.raise_for_status()
    return response.json()
```

`@retry` convierte la función en una que reintenta automáticamente.
La función en sí no sabe que está siendo reintentada — escribe solo la
lógica de una llamada. Tenacity gestiona el bucle, los tiempos y la
propagación del error final.

### Parámetros principales

| Parámetro | Comportamiento |
|---|---|
| `stop_after_attempt(n)` | Máximo `n` intentos totales |
| `wait_fixed(s)` | Espera fija de `s` segundos entre intentos |
| `wait_exponential(min, max)` | Espera que dobla cada intento, con mínimo y tope |
| `retry_if_exception_type(T)` | Solo reintenta si la excepción es del tipo `T` |
| `reraise=True` | Propaga la excepción original al agotar los intentos |

**Por qué `wait_exponential` en lugar de `wait_fixed`:**
Un servidor bajo carga que falla no se recupera si recibe el mismo volumen
de peticiones inmediatamente. La espera exponencial da tiempo al servidor
para estabilizarse, y reduce la presión acumulada de múltiples clientes
reintentando a la vez.

---

▶ Ejecuta el ejemplo:
  uv run python scripts/clase_03/conceptos/04_tenacity_retry.py

---

### Análisis de 04_tenacity_retry.py

**Por qué `intentos_realizados` es una variable global:**
El decorador `@retry` llama a `llamar_api_externa()` múltiples veces como
llamadas independientes. La función necesita "recordar" cuántas veces fue
invocada para simular el fallo en las primeras tres. Una variable global
persiste entre llamadas del mismo proceso — en producción, este patrón
se reemplaza por un estado externo real (el servidor que falla).

**Qué ocurre con los tiempos:**
`wait_exponential(min=1, max=10)` hace que tenacity espere 1s entre el
intento 1 y 2, 2s entre el 2 y 3, 4s entre el 3 y 4. El script real
tardará ~7 segundos en completarse. Es el coste de reintentar ante fallos
transitorios — visible y controlado.

**Qué pasa si todos los intentos fallan:**
Si `intentos_realizados` nunca alcanzara 4, el cuarto intento también fallaría.
Tenacity agotan los 4 intentos y propaga la última `ConnectionError` al bloque
`try/except` externo, que imprime el mensaje de fallo definitivo.
