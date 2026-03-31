"""Historial de consultas usando collections.deque.

deque con maxlen descarta automáticamente las entradas más antiguas
cuando se supera la capacidad — O(1) para append y popleft.
"""

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger


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
