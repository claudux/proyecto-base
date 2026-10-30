"""Configuración explícita para desacoplar el cliente del entorno en las pruebas."""

import os
from dataclasses import dataclass, field
from math import isfinite

from dotenv import load_dotenv


MODELO_PREDETERMINADO = "gemini-3.5-flash-lite"


@dataclass(frozen=True)
class Tarifas:
    """Precios estimados en USD por millón de tokens."""

    entrada_por_millon: float = 0.30
    salida_por_millon: float = 2.50

    def __post_init__(self) -> None:
        for valor in (self.entrada_por_millon, self.salida_por_millon):
            if isinstance(valor, bool) or not isfinite(valor) or valor < 0:
                raise ValueError("Las tarifas deben ser números finitos no negativos.")


@dataclass(frozen=True)
class Configuracion:
    api_key: str
    modelo: str = MODELO_PREDETERMINADO
    timeout_segundos: float = 30.0
    tarifas: Tarifas = field(default_factory=Tarifas)

    def __post_init__(self) -> None:
        if not isinstance(self.api_key, str) or not self.api_key.strip() or self.api_key == "tu_llave_aqui":
            raise ValueError("Configura una GEMINI_API_KEY válida.")
        if not isinstance(self.modelo, str) or not self.modelo.strip():
            raise ValueError("El modelo no puede estar vacío.")
        if not isfinite(self.timeout_segundos) or self.timeout_segundos <= 0:
            raise ValueError("El timeout debe ser mayor que cero.")

    @classmethod
    def desde_entorno(cls) -> "Configuracion":
        load_dotenv()
        modelo = os.getenv("GEMINI_MODEL") or MODELO_PREDETERMINADO
        if modelo == MODELO_PREDETERMINADO:
            tarifas = Tarifas()
        else:
            entrada = os.getenv("GEMINI_PRECIO_ENTRADA_POR_MILLON")
            salida = os.getenv("GEMINI_PRECIO_SALIDA_POR_MILLON")
            if entrada is None or salida is None:
                raise ValueError("Para otro modelo, configura ambas tarifas por millón de tokens.")
            tarifas = Tarifas(float(entrada), float(salida))
        return cls(api_key=os.getenv("GEMINI_API_KEY", ""), modelo=modelo, tarifas=tarifas)
