"""
Ejercicios — Clase 08: Arquitectura Hexagonal — Protocol e Inyección de Dependencias
=====================================================================================
Cinco ejercicios sobre typing.Protocol, duck typing e inyección por constructor.

Ejecutar (desde curso/):
    uv run python scripts/clase_08/ejercicios_clase_08.py

Requisito: autocontenido, sin imports de pycommute.
"""

from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Ejercicio 1
# ---------------------------------------------------------------------------

# TODO: Ejercicio 1 — Definir un Protocol con un método abstracto
# Define el Protocol `Notificador` (decorado con @runtime_checkable) que declare:
#   - método `enviar(self, mensaje: str) -> bool`
#     (retorna True si el envío fue exitoso, False si no)
# Pista: repasa la seccion 2 "typing.Protocol — contratos sin herencia" en 01_conceptos.md
#        y el script scripts/clase_08/conceptos/01_protocol_basico.py


# ---------------------------------------------------------------------------
# Ejercicio 2
# ---------------------------------------------------------------------------

# TODO: Ejercicio 2 — Implementar dos clases que satisfacen el mismo Protocol
# Implementa DOS clases sin herencia de Notificador:
#   - `NotificadorEmail`: su método `enviar` imprime "Email: {mensaje}" y retorna True
#   - `NotificadorSMS`: su método `enviar` imprime "SMS: {mensaje}" y retorna True
# Ninguna de las dos hereda de Notificador — deben satisfacerlo por duck typing.
# Pista: repasa la seccion 2 "Implementar un Protocol" en 01_conceptos.md
#        y el script scripts/clase_08/conceptos/01_protocol_basico.py


# ---------------------------------------------------------------------------
# Ejercicio 3
# ---------------------------------------------------------------------------

# TODO: Ejercicio 3 — Función que acepta el Protocol
# Implementa `notificar_usuario` que:
#   - Recibe `notificador: Notificador` y `mensaje: str`
#   - Llama a notificador.enviar(mensaje)
#   - Retorna True si el envío fue exitoso, False si no
# La función funciona con CUALQUIER objeto que implemente Notificador.
# Pista: repasa la seccion 2 "Funcion que usa el Protocol" en 01_conceptos.md
#        y el script scripts/clase_08/conceptos/01_protocol_basico.py
def notificar_usuario(notificador, mensaje: str) -> bool:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 4
# ---------------------------------------------------------------------------

# TODO: Ejercicio 4 — DI por constructor
# Implementa la clase `ServicioAlertas` con:
#   - `__init__(self, notificador: Notificador) -> None`:
#       guarda el notificador como atributo `self._notificador`
#   - `alerta_temperatura(self, ciudad: str, temp: float) -> bool`:
#       si temp > 35, envía "¡Alerta! {ciudad}: {temp}°C" y retorna True
#       si no, retorna False sin enviar nada
# El notificador se inyecta, no se instancia dentro de la clase.
# Pista: repasa la seccion 3 "Inyeccion de dependencias por constructor" en 01_conceptos.md
#        y el script scripts/clase_08/conceptos/02_inyeccion_dependencias.py
class ServicioAlertas:
    def __init__(self, notificador) -> None:
        pass  # ← reemplazar con tu implementación

    def alerta_temperatura(self, ciudad: str, temp: float) -> bool:
        pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Ejercicio 5
# ---------------------------------------------------------------------------

# TODO: Ejercicio 5 — Factory function que inyecta la implementación correcta
# Implementa `crear_servicio_alertas` que:
#   - Recibe `canal: str` ("email" o "sms")
#   - Si canal == "email": crea NotificadorEmail y lo inyecta en ServicioAlertas
#   - Si canal == "sms":   crea NotificadorSMS y lo inyecta en ServicioAlertas
#   - Si canal no es conocido: lanza ValueError(f"Canal desconocido: {canal}")
#   - Retorna la instancia de ServicioAlertas configurada
# Pista: repasa la seccion 3 "Factory como punto de composicion" en 01_conceptos.md
#        y el script scripts/clase_08/conceptos/02_inyeccion_dependencias.py
def crear_servicio_alertas(canal: str) -> ServicioAlertas:
    pass  # ← reemplazar con tu implementación


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo() -> None:
    print("=== Ejercicio 1 y 2: Protocol y clases ===")
    try:
        email = NotificadorEmail()  # type: ignore[name-defined]
        sms = NotificadorSMS()  # type: ignore[name-defined]
        print(f"  NotificadorEmail es Notificador: {isinstance(email, Notificador)}")  # type: ignore[name-defined]
        print(f"  NotificadorSMS es Notificador:   {isinstance(sms, Notificador)}")  # type: ignore[name-defined]
    except NameError:
        print("  Sin implementar aún.")

    print("\n=== Ejercicio 3: notificar_usuario ===")
    try:
        ok = notificar_usuario(NotificadorEmail(), "Prueba de email")  # type: ignore[name-defined]
        print(f"  Resultado: {ok}")
    except (NameError, TypeError):
        print("  Sin implementar aún.")

    print("\n=== Ejercicio 4: ServicioAlertas ===")
    try:
        servicio = ServicioAlertas(NotificadorEmail())  # type: ignore[name-defined]
        enviado = servicio.alerta_temperatura("Valencia", 38.0)
        no_enviado = servicio.alerta_temperatura("Valencia", 25.0)
        print(f"  38°C -> alerta enviada: {enviado}")
        print(f"  25°C -> alerta enviada: {no_enviado}")
    except (NameError, TypeError):
        print("  Sin implementar aún.")

    print("\n=== Ejercicio 5: crear_servicio_alertas ===")
    try:
        svc_email = crear_servicio_alertas("email")
        svc_sms = crear_servicio_alertas("sms")
        svc_email.alerta_temperatura("Madrid", 36.0)
        svc_sms.alerta_temperatura("Barcelona", 37.0)
        print("  Factory funcionando correctamente.")
        try:
            crear_servicio_alertas("fax")
        except ValueError as e:
            print(f"  Canal invalido capturado: {e}")
    except (NameError, TypeError, AttributeError):
        print("  Sin implementar aún.")


if __name__ == "__main__":
    demo()
