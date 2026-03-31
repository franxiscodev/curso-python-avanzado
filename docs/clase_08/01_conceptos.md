# Clase 08 — Conceptos: Arquitectura Hexagonal

## 1. El problema del acoplamiento

Imagina una función que necesita enviar un email cuando ocurre algo:

```python
# Version acoplada
import smtplib

def procesar_pedido(pedido_id: str) -> None:
    # ... logica del pedido ...
    with smtplib.SMTP("smtp.gmail.com") as servidor:
        servidor.sendmail("origen", "destino", f"Pedido {pedido_id} procesado")
```

Para testear `procesar_pedido`, necesitas un servidor SMTP real. Si mañana cambias a SendGrid, tienes que tocar `procesar_pedido`. La logica de negocio y la infraestructura están mezcladas.

**El problema:** el código que hace algo (logica) conoce demasiado sobre el código que lo ayuda (infraestructura).

---

## 2. Arquitectura Hexagonal

La Arquitectura Hexagonal (Alistair Cockburn, 2005) resuelve este problema con una regla simple:

> **El núcleo de la aplicación no depende de la infraestructura. La infraestructura depende del núcleo.**

```
                 ┌─────────────────┐
  Tests ─────────┤                 ├──── Base de datos
                 │   NUCLEO        │
  CLI  ─────────┤   (logica pura)  ├──── API externa
                 │                 │
  HTTP ─────────┤                 ├──── Cache
                 └─────────────────┘
                      Puertos
```

Cada flecha en el diagrama representa un **puerto** — un contrato que define cómo se comunican el núcleo y el mundo exterior.

**Analogía:** los adaptadores de enchufe de viaje. Tu laptop (núcleo) no cambia cuando viajas a UK — solo cambias el adaptador. La Arquitectura Hexagonal hace lo mismo con el software.

---

## 3. typing.Protocol — duck typing estructural

`Protocol` permite definir contratos de comportamiento sin forzar herencia:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Notificador(Protocol):
    def enviar(self, mensaje: str, destinatario: str) -> bool: ...
```

Cualquier clase que tenga el método `enviar(self, mensaje, destinatario) -> bool` **automáticamente satisface** este Protocol, sin heredar de él:

```python
class EmailNotificador:
    def enviar(self, mensaje: str, destinatario: str) -> bool:
        print(f"EMAIL a {destinatario}: {mensaje}")
        return True

class SMSNotificador:
    def enviar(self, mensaje: str, destinatario: str) -> bool:
        print(f"SMS  a {destinatario}: {mensaje}")
        return True

# Ambas satisfacen Notificador sin escribir "class Foo(Notificador):"
```

**Duck typing estructural:** si el objeto tiene los métodos correctos, puede usarse en cualquier lugar que espere ese Protocol.

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_08/conceptos/01_protocol_basico.py
```

---

## 4. @runtime_checkable

Por defecto, `isinstance(obj, MiProtocol)` lanza `TypeError`. Con `@runtime_checkable`, funciona en tiempo de ejecución:

```python
notificador_email = EmailNotificador()
notificador_sms   = SMSNotificador()

isinstance(notificador_email, Notificador)  # True
isinstance(notificador_sms, Notificador)    # True
isinstance("hola", Notificador)             # False — str no tiene enviar()
```

> **Nota:** la verificación en runtime solo comprueba que los métodos existen, no sus firmas. La verificación completa la hace el type checker (mypy/pyright).

---

## 5. Inyeccion de Dependencias (DI)

La Inyeccion de Dependencias resuelve el acoplamiento pasando las dependencias desde fuera, no creándolas internamente:

```python
# SIN DI — la clase crea su propia dependencia
class ReporteService:
    def __init__(self):
        self._notificador = EmailNotificador()  # acoplado a Email

# CON DI — la dependencia viene de fuera
class ReporteService:
    def __init__(self, notificador: Notificador) -> None:
        self._notificador = notificador  # no sabe qué implementacion es
```

**Constructor injection:** las dependencias se pasan al crear el objeto. Es el patrón más común y el más claro.

```python
# En produccion — adaptador real
servicio_prod = ReporteService(notificador=EmailNotificador())

# En tests — adaptador simulado
servicio_test = ReporteService(notificador=NotificadorFake())
```

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_08/conceptos/02_inyeccion_dependencias.py
```

---

## 6. DI y testing — mocks sin parchear módulos

Con DI, los tests pasan el mock directamente — no necesitan `mocker.patch`:

```python
class NotificadorFake:
    """Captura mensajes sin enviar nada real."""
    def __init__(self) -> None:
        self.enviados: list[str] = []

    def enviar(self, mensaje: str, destinatario: str) -> bool:
        self.enviados.append(mensaje)
        return True

def test_servicio_notifica_al_confirmar() -> None:
    fake = NotificadorFake()
    servicio = ReporteService(notificador=fake)

    servicio.confirmar_pedido("A001")

    assert len(fake.enviados) == 1
    assert "A001" in fake.enviados[0]
```

Sin `mocker.patch`. Sin interceptar módulos. El test construye el servicio con sus dependencias explícitamente.

---

## 7. La regla de dependencia

En Arquitectura Hexagonal, las dependencias siempre apuntan **hacia el núcleo**:

```
adapters/weather.py  →  importa  →  core/ports.py
adapters/route.py    →  importa  →  core/ports.py
services/commute.py  →  importa  →  core/ports.py

# NUNCA al reves:
core/ports.py        ✗  NO importa  ✗  adapters/weather.py
```

**Por qué importa:** si `core/ports.py` importase `adapters/weather.py`, el núcleo dependería de `httpx`, de la URL de OpenWeather, de la API key — infraestructura que puede cambiar. Al prohibir esa dirección, el núcleo permanece puro.

```
Flujo correcto de imports:
    adapters/   →   core/
    services/   →   core/
    tests/      →   adapters/, services/, core/
```

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_08/conceptos/03_regla_dependencia.py
```

---

## 8. Arquitectura completa en miniatura

El script `04_hexagonal_completo.py` muestra los tres componentes juntos (Puertos, Adaptadores, Servicio) en ~100 lineas sin dependencias externas.

▶ Ejecuta el ejemplo:
```
uv run scripts/clase_08/conceptos/04_hexagonal_completo.py
```

---

## Resumen visual

```
┌─────────────────────────────────────────────────────────┐
│                       NUCLEO                            │
│                                                         │
│  core/ports.py ← contratos de comportamiento           │
│  core/ranking.py ← logica de ordenamiento              │
│  core/history.py ← logica de historial                 │
│  services/commute.py ← orquestacion (usa Ports)        │
│                                                         │
└──────────────────────┬──────────────────────────────────┘
                       │ los adaptadores implementan los puertos
┌──────────────────────▼──────────────────────────────────┐
│                    ADAPTADORES                          │
│                                                         │
│  adapters/weather.py ← OpenWeatherAdapter              │
│  adapters/route.py   ← OpenRouteAdapter                │
│  adapters/cache.py   ← MemoryCacheAdapter              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Regla de oro:** `core/` no tiene imports de `adapters/`. `adapters/` puede importar de `core/`.
