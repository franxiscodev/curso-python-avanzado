"""
deque con maxlen — Buffer circular para eventos del sistema
==========================================================
Demuestra deque(maxlen=N) como ring buffer: cuando el buffer está
lleno y se añade un nuevo evento, el más antiguo se descarta automáticamente.

Conceptos que ilustra:
- deque(maxlen=N): activa el modo ring buffer; no es necesario gestionar
  el tamaño manualmente — la estructura lo hace sola.
- append() con buffer lleno: descarta el elemento del lado izquierdo
  (el más antiguo) y añade el nuevo al lado derecho. Todo en O(1).
- SystemEvent como @dataclass: genera __init__ y __repr__ automáticamente
  sin boilerplate.
- Uso real: retener las últimas N métricas, logs o eventos de un stream
  sin acumular memoria ilimitada.

Ejecutar:
    uv run python scripts/clase_07/conceptos/03_deque_basico.py
"""
from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass
class SystemEvent:
    event_id: int
    payload: dict[str, Any]


class EventBuffer:
    def __init__(self, max_capacity: int = 5):
        # maxlen convierte el deque en un ring buffer nativo en C.
        # Cuando se llena, append() descarta el evento más antiguo sin error.
        self._buffer: deque[SystemEvent] = deque(maxlen=max_capacity)

    def ingest(self, event: SystemEvent) -> None:
        """Ingiere un evento. Si el buffer está lleno, descarta el más antiguo."""
        self._buffer.append(event)

    def show_snapshot(self) -> None:
        print(
            f"Estado del Buffer (Ocupacion: {len(self._buffer)}/{self._buffer.maxlen}):")
        for ev in self._buffer:
            print(f"  -> Evento {ev.event_id}: {ev.payload}")
        print("-" * 40)


def main():
    stream = EventBuffer(max_capacity=3)

    # Metemos 5 eventos en un buffer de capacidad 3.
    # Los eventos 1 y 2 serán descartados cuando lleguen 4 y 5.
    print("Iniciando ingesta de metricas (Capacidad estricta: 3)...\n")
    for i in range(1, 6):
        print(f"Ingiriendo Evento {i}...")
        stream.ingest(SystemEvent(event_id=i, payload={"cpu": 40 + i}))
        stream.show_snapshot()


if __name__ == "__main__":
    main()
