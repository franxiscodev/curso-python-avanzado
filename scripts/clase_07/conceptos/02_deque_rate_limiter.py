"""
deque — Rate limiter con ventana deslizante
============================================
Implementa un rate limiter que permite un máximo de N peticiones
en una ventana de tiempo deslizante usando deque.

Conceptos que ilustra:
- deque sin maxlen: actúa como historial de timestamps; el tamaño
  se controla manualmente descartando entradas fuera de la ventana.
- popleft() en O(1): elimina las entradas antiguas sin desplazar
  el resto (a diferencia de list.pop(0) que es O(n)).
- Sliding window: cada llamada a allow_request() limpia el historial
  hasta el límite de time_window segundos atrás y luego decide.
- El patrón es la base de rate limiters reales en APIs de producción.

Ejecutar:
    uv run python scripts/clase_07/conceptos/02_deque_rate_limiter.py
"""
import time
from collections import deque


class RateLimiter:
    def __init__(self, max_requests: int, time_window_seconds: int):
        self.max_requests = max_requests
        self.time_window = time_window_seconds
        # deque sin maxlen: gestionamos el tamaño por tiempo, no por cantidad fija
        self.history: deque[float] = deque()

    def allow_request(self) -> bool:
        now = time.time()

        # 1. Limpieza (Sliding Window): O(1) por cada elemento eliminado.
        # Descartamos timestamps que quedaron fuera de la ventana de tiempo.
        while self.history and self.history[0] <= now - self.time_window:
            self.history.popleft()

        # 2. Verificación y registro
        if len(self.history) < self.max_requests:
            self.history.append(now)  # O(1) — append siempre al lado derecho
            return True
        return False


def main():
    # Permite 3 peticiones por cada 2 segundos
    limiter = RateLimiter(max_requests=3, time_window_seconds=2)

    print("Iniciando proteccion de Rate Limit (Max 3 req/2s)...")
    for i in range(5):
        allowed = limiter.allow_request()
        status = "[OK] ACEPTADA" if allowed else "[BLOQUEADA] Too Many Requests"
        print(f"Peticion {i+1} -> {status}")
        time.sleep(0.1)  # Rafaga rapida — todas dentro de la misma ventana

    print("[ESPERA] 2 segundos para que la ventana se limpie...")
    time.sleep(2)

    # Tras la espera, el historial esta vacio -> la peticion pasa
    resultado = "[OK] ACEPTADA" if limiter.allow_request() else "[BLOQUEADA]"
    print(f"Peticion 6 -> {resultado}")


if __name__ == "__main__":
    main()
