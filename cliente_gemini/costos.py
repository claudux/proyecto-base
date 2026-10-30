"""Costo estimado por operación y total de esta instancia del cliente."""

from dataclasses import dataclass, field
from typing import Any

from .configuracion import Tarifas
from .errores import ErrorProveedor


@dataclass(frozen=True)
class OperacionCosto:
    tokens_entrada: int
    tokens_salida: int
    tokens_razonamiento: int
    tokens_totales: int
    usd_estimados: float


def _conteo(uso: dict[str, Any], campo: str, *, predeterminado: int | None = None) -> int:
    valor = uso.get(campo, predeterminado)
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        raise ErrorProveedor(f"usageMetadata.{campo} falta o no es un entero no negativo.")
    return valor


@dataclass
class RegistroCostos:
    """Estado por cliente; evita un acumulador global compartido entre pruebas."""

    tarifas: Tarifas
    operaciones: list[OperacionCosto] = field(default_factory=list)

    def registrar(self, respuesta: dict[str, Any]) -> OperacionCosto:
        uso = respuesta.get("usageMetadata")
        if not isinstance(uso, dict):
            raise ErrorProveedor("La respuesta no incluye usageMetadata válido.")
        entrada = _conteo(uso, "promptTokenCount")
        salida = _conteo(uso, "candidatesTokenCount")
        razonamiento = _conteo(uso, "thoughtsTokenCount", predeterminado=0)
        total = _conteo(uso, "totalTokenCount")
        costo = (
            entrada * self.tarifas.entrada_por_millon
            + (salida + razonamiento) * self.tarifas.salida_por_millon
        ) / 1_000_000
        operacion = OperacionCosto(entrada, salida, razonamiento, total, costo)
        self.operaciones.append(operacion)
        return operacion

    @property
    def costo_total_sesion(self) -> float:
        return sum(operacion.usd_estimados for operacion in self.operaciones)

    @property
    def ultima_operacion(self) -> OperacionCosto | None:
        return self.operaciones[-1] if self.operaciones else None
