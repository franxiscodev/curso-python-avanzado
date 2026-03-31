"""Concepto 02 — Inyeccion de Dependencias (DI) por constructor.

Sin DI: la clase instancia sus dependencias internamente — imposible de testear.
Con DI: las dependencias se pasan desde fuera — testeable, flexible, SOLID.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_08/conceptos/02_inyeccion_dependencias.py

    # Linux
    uv run scripts/clase_08/conceptos/02_inyeccion_dependencias.py
"""

from typing import Protocol


# --- Puerto (contrato) ---

class NotificadorPort(Protocol):
    def enviar(self, mensaje: str) -> None:
        ...


# --- Adaptadores concretos ---

class EmailNotificador:
    def enviar(self, mensaje: str) -> None:
        print(f"  [EMAIL] {mensaje}")


class SmsNotificador:
    def enviar(self, mensaje: str) -> None:
        print(f"  [SMS]   {mensaje}")


class NotificadorFake:
    """Notificador para tests — registra mensajes sin enviar nada real."""

    def __init__(self) -> None:
        self.enviados: list[str] = []

    def enviar(self, mensaje: str) -> None:
        self.enviados.append(mensaje)


# --- MAL: sin DI — dependencia acoplada internamente ---

class ServicioPedidoSinDI:
    def __init__(self) -> None:
        self._notificador = EmailNotificador()  # hardcodeado

    def confirmar(self, pedido_id: str) -> None:
        self._notificador.enviar(f"Pedido {pedido_id} confirmado")


# --- BIEN: con DI por constructor ---

class ServicioPedido:
    def __init__(self, notificador: NotificadorPort) -> None:
        self._notificador = notificador  # inyectado desde fuera

    def confirmar(self, pedido_id: str) -> None:
        self._notificador.enviar(f"Pedido {pedido_id} confirmado")


# --- Demo ---

print("=== Sin DI (notificador hardcodeado) ===")
servicio_sin_di = ServicioPedidoSinDI()
servicio_sin_di.confirmar("A001")
# Para testear hay que parchear la clase interna — fragil

print()
print("=== Con DI — adaptador real ===")
servicio_email = ServicioPedido(notificador=EmailNotificador())
servicio_email.confirmar("B001")

servicio_sms = ServicioPedido(notificador=SmsNotificador())
servicio_sms.confirmar("B002")

print()
print("=== Con DI — adaptador fake para tests ===")
fake = NotificadorFake()
servicio_test = ServicioPedido(notificador=fake)
servicio_test.confirmar("C001")
servicio_test.confirmar("C002")

print(f"Mensajes capturados: {fake.enviados}")
assert fake.enviados[0] == "Pedido C001 confirmado"
assert fake.enviados[1] == "Pedido C002 confirmado"
print("Assertions OK — test sin parchear nada")
