"""
deque vs list — Benchmark de inserción frontal
================================================
Mide el impacto de usar list.insert(0) frente a deque.appendleft()
para 250,000 inserciones al frente de la colección.

Conceptos que ilustra:
- list.insert(0): O(n) — desplaza todos los elementos para mantener
  la contigüidad en memoria. Se vuelve lento con colecciones grandes.
- deque.appendleft(): O(1) — actualiza un puntero en la lista
  doblemente enlazada. Sin desplazamientos, coste constante.
- El benchmark hace visible la diferencia de complejidad algorítmica:
  ambas estructuras son correctas, pero una bloquea mientras la otra no.
- Regla práctica: si insertas o extraes del frente con frecuencia, usa deque.

Ejecutar:
    uv run python scripts/clase_07/conceptos/04_deque_vs_lista.py
"""
import time
from collections import deque

# Un número lo suficientemente alto para causar dolor real en la CPU
LOAD_SIZE = 250_000


def stress_list(items: int) -> float:
    lista_dinamica = []
    start = time.perf_counter()
    for i in range(items):
        # El peor escenario posible para un array: insertar en el índice 0.
        # Python debe desplazar todos los elementos existentes una posición.
        lista_dinamica.insert(0, i)
    return time.perf_counter() - start


def stress_deque(items: int) -> float:
    cola_eficiente = deque()
    start = time.perf_counter()
    for i in range(items):
        # Inserción O(1): actualiza el puntero izquierdo del bloque enlazado.
        cola_eficiente.appendleft(i)
    return time.perf_counter() - start


def main():
    print(f"Iniciando prueba de estres ({LOAD_SIZE:,} inserciones frontales)")
    print("Observa como el script se detiene durante la prueba de lista...\n")

    # 1. Prueba con Lista — O(n) por inserción
    print("[LISTA] Ejecutando List insert(0)... esto va a doler...")
    tiempo_lista = stress_list(LOAD_SIZE)
    print(f"[LISTA] Tiempo: {tiempo_lista:.4f} segundos")

    # 2. Prueba con Deque — O(1) por inserción
    print("\n[DEQUE] Ejecutando Deque appendleft()...")
    tiempo_deque = stress_deque(LOAD_SIZE)
    print(f"[DEQUE] Tiempo: {tiempo_deque:.4f} segundos")

    # Análisis de impacto
    factor = tiempo_lista / tiempo_deque if tiempo_deque > 0 else 0
    print("-" * 50)
    print(f"[RESULTADO] Deque fue {factor:,.0f} veces mas rapido.")
    print("Si esto fuera una API, la lista habria bloqueado todas las conexiones HTTP.")


if __name__ == "__main__":
    main()
