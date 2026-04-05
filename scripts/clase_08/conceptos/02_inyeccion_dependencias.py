"""
Concepto 2: Inyección de dependencias por constructor.

CachePort define el contrato: get(key) y set(key, value).
DictCacheAdapter implementa el contrato con un dict en memoria.
CommuteService recibe un CachePort en el constructor — no crea
ni importa ningún adaptador concreto.

Por qué recibir la interfaz y no instanciarla internamente:
- En producción: CommuteService(cache=DictCacheAdapter())
- En tests:      CommuteService(cache=FakeCacheAdapter())
  Sin mocker.patch, sin interceptar módulos.

El demo muestra cache hit/miss: la segunda llamada con "ruta_01"
devuelve el resultado guardado sin recalcular.

Conexión con el proyecto:
  services/commute.py recibe WeatherPort, RoutePort y CachePort
  exactamente así — ningún adaptador se instancia dentro del servicio.
  La factory demo_proyecto.py o el test crean los adaptadores y los inyectan.

Ejecutar:
  uv run python scripts/clase_08/conceptos/02_inyeccion_dependencias.py
"""

from typing import Optional, Protocol


class CachePort(Protocol):
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str) -> None: ...


class DictCacheAdapter:
    def __init__(self):
        self._store = {}

    def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    def set(self, key: str, value: str) -> None:
        self._store[key] = value


class CommuteService:
    # EL SECRETO ESTÁ AQUÍ: Recibir la interfaz en el constructor
    def __init__(self, cache: CachePort):
        self.cache = cache

    def get_commute_info(self, route_id: str) -> str:
        cached_data = self.cache.get(route_id)
        if cached_data:
            return f"Cache Hit: {cached_data}"

        # Simula un cálculo pesado
        result = "Datos procesados de la ruta"
        self.cache.set(route_id, result)
        return f"Calculado Nuevo: {result}"


# Ejecución (Capa externa / main.py)
memory_cache = DictCacheAdapter()
# Inyectamos la dependencia
service = CommuteService(cache=memory_cache)

print(service.get_commute_info("ruta_01"))  # Calculado Nuevo
print(service.get_commute_info("ruta_01"))  # Cache Hit
