"""Política reutilizable de reintento, independiente de HTTP y de Gemini."""

import logging
import random
import time
from dataclasses import dataclass
from math import isfinite
from typing import Callable, TypeVar

from .errores import ErrorTemporal


T = TypeVar("T")
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PoliticaReintentos:
    intentos: int = 3
    espera_base: float = 2.0
    espera_maxima: float = 30.0
    jitter_proporcion: float = 0.1

    def __post_init__(self) -> None:
        if isinstance(self.intentos, bool) or self.intentos < 1:
            raise ValueError("Debe permitirse al menos un intento.")
        for valor in (self.espera_base, self.espera_maxima, self.jitter_proporcion):
            if not isfinite(valor) or valor < 0:
                raise ValueError("Las esperas y el jitter deben ser finitos y no negativos.")
        if self.espera_maxima < self.espera_base:
            raise ValueError("La espera máxima no puede ser menor que la base.")


class Reintentador:
    def __init__(
        self,
        politica: PoliticaReintentos | None = None,
        *,
        dormir: Callable[[float], None] = time.sleep,
        aleatorio: Callable[[float, float], float] = random.uniform,
    ) -> None:
        self._politica = politica or PoliticaReintentos()
        self._dormir = dormir
        self._aleatorio = aleatorio

    def ejecutar(self, operacion: Callable[[], T]) -> T:
        for intento in range(1, self._politica.intentos + 1):
            try:
                return operacion()
            except ErrorTemporal as error:
                if intento == self._politica.intentos:
                    raise
                base = min(
                    self._politica.espera_base * 2 ** (intento - 1),
                    self._politica.espera_maxima,
                )
                espera = min(
                    base + self._aleatorio(0, base * self._politica.jitter_proporcion),
                    self._politica.espera_maxima,
                )
                if error.retry_after is not None:
                    # Una instrucción explícita del proveedor tiene prioridad sobre el techo local.
                    espera = max(espera, error.retry_after)
                LOGGER.warning("Intento %s/%s falló; reintento en %.2f s", intento, self._politica.intentos, espera)
                self._dormir(espera)
        raise AssertionError("Bucle de reintentos sin resultado")
