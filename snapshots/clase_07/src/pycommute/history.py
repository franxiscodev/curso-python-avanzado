"""Historial de consultas usando collections.deque.

deque con maxlen descarta automáticamente las entradas más antiguas
cuando se supera la capacidad — O(1) para append y popleft.
"""

# [CLASE 7] Módulo nuevo — introduce deque y dataclasses.
# Por qué deque y no list: list.pop(0) es O(n) — mueve todos los elementos.
# deque(maxlen=N).append() descarta el elemento más antiguo en O(1) automáticamente.
#
# Por qué dataclass para ConsultaEntry: genera __init__, __repr__, __eq__
# automáticamente. Es el paso previo a Pydantic V2 en Clase 9 — misma idea,
# más potencia de validación.
#
# [CLASE 9 →] ConsultaEntry se convertirá en un modelo Pydantic V2 con
#             validación de tipos, serialización JSON y campos con defaults.

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger


# [CLASE 7] @dataclass genera __init__(timestamp, city, profiles, weather, routes)
# automáticamente. Sin el decorador habría que escribirlo a mano.
# Antes (Clase 6 y anteriores): los datos de consulta se pasaban como dicts sueltos.
@dataclass
class ConsultaEntry:
    """Entrada del historial de consultas.

    Attributes:
        timestamp: Momento de la consulta.
        city: Ciudad consultada.
        profiles: Perfiles de ruta consultados.
        weather: Datos de clima obtenidos.
        routes: Rutas obtenidas.
    """

    timestamp: datetime
    city: str
    profiles: list[str]
    weather: dict[str, Any]
    routes: list[dict[str, Any]]

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M")
        profiles_str = ", ".join(self.profiles)
        return f"[{ts}] {self.city} -> {profiles_str}"


class ConsultaHistory:
    """Historial de consultas con capacidad máxima configurable.

    Usa deque(maxlen=N) para descartar automáticamente
    las consultas más antiguas cuando se supera la capacidad.
    """

    def __init__(self, maxlen: int = 10) -> None:
        """Inicializa el historial con capacidad máxima.

        Args:
            maxlen: Número máximo de entradas a mantener.
        """
        # [CLASE 7] deque(maxlen=N): cuando se llena y se hace append(),
        # el elemento más antiguo (el de la izquierda) se descarta en O(1).
        self._history: deque[ConsultaEntry] = deque(maxlen=maxlen)

    def add(
        self,
        city: str,
        profiles: list[str],
        weather: dict[str, Any],
        routes: list[dict[str, Any]],
    ) -> None:
        """Agrega una consulta al historial.

        Args:
            city: Ciudad consultada.
            profiles: Perfiles de ruta consultados.
            weather: Datos de clima obtenidos.
            routes: Rutas obtenidas.
        """
        entry = ConsultaEntry(
            timestamp=datetime.now(),
            city=city,
            profiles=profiles,
            weather=weather,
            routes=routes,
        )
        self._history.append(entry)
        logger.debug(
            "Historial actualizado: {n}/{max} entradas",
            n=len(self._history),
            max=self._history.maxlen,
        )

    def get_recent(self, n: int | None = None) -> list[ConsultaEntry]:
        """Obtiene las consultas más recientes.

        Args:
            n: Número de entradas. None devuelve todas.

        Returns:
            Lista de entradas — la más reciente primero.
        """
        entries = list(self._history)
        entries.reverse()
        return entries[:n] if n else entries

    def __len__(self) -> int:
        return len(self._history)

    def clear(self) -> None:
        """Limpia el historial."""
        self._history.clear()
