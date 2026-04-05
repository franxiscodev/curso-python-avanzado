"""
heapq — Cola de prioridad con dataclass
=========================================
Demuestra el uso de heapq como cola de prioridad para procesar
peticiones de API según su nivel de urgencia.

Conceptos que ilustra:
- @dataclass(order=True): habilita la comparación (<) entre instancias;
  heapq usa este orden para mantener el invariante del heap.
- field(compare=False): excluye 'payload' de las comparaciones,
  evitando TypeError si dos peticiones tienen la misma prioridad y timestamp.
- heappush / heappop: O(log n) para insertar y extraer el mínimo.
- Desempate por timestamp: dentro de la misma prioridad, la petición
  más antigua (menor timestamp) se procesa primero (FIFO natural).

Ejecutar:
    uv run python scripts/clase_07/conceptos/01_heapq_basico.py
"""
import heapq
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class ApiRequest:
    # El orden de los atributos importa para la comparación de heapq.
    # Primero compara prioridad (menor número = más urgente).
    prioridad: int

    # Segundo compara timestamp para desempate (FIFO dentro de la misma prioridad).
    timestamp: float = field(default_factory=time.time)

    # Campo ignorado en la ordenación, contiene la carga útil.
    payload: dict[str, Any] = field(compare=False, default_factory=dict)


def main():
    cola_peticiones: list[ApiRequest] = []

    # Simulamos peticiones llegando en distinto orden
    # Premium = 1, Estandar = 2, Background = 3
    heapq.heappush(cola_peticiones, ApiRequest(
        prioridad=2, payload={"user": "juan_free", "action": "read"}))
    time.sleep(0.01)  # Forzamos diferencia en timestamp
    heapq.heappush(cola_peticiones, ApiRequest(prioridad=1, payload={
                   "user": "maria_premium", "action": "write"}))
    time.sleep(0.01)
    heapq.heappush(cola_peticiones, ApiRequest(
        prioridad=1, payload={"user": "ceo_admin", "action": "delete"}))

    # heappop garantiza que siempre sale la peticion mas prioritaria
    print("Procesando peticiones por prioridad (Min-Heap):")
    while cola_peticiones:
        # Extraemos siempre la petición más prioritaria en O(log n)
        req = heapq.heappop(cola_peticiones)
        print(
            f"[{req.prioridad}] Procesando: {req.payload['user']} - {req.payload['action']}")


if __name__ == "__main__":
    main()
