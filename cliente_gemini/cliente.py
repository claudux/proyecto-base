"""Interfaz pública que coordina piezas sin duplicar sus responsabilidades."""

from typing import Any

from .configuracion import Configuracion
from .costos import RegistroCostos
from .errores import ErrorServicioAgotado, ErrorTemporal
from .peticiones import armar_peticion
from .reintentos import Reintentador
from .respuestas import extraer_texto, parsear_respuesta_json
from .transporte import TransporteGemini


class ClienteGemini:
    def __init__(
        self,
        configuracion: Configuracion,
        *,
        transporte: TransporteGemini | None = None,
        reintentador: Reintentador | None = None,
        registro_costos: RegistroCostos | None = None,
    ) -> None:
        self._transporte = transporte or TransporteGemini(configuracion)
        self._reintentador = reintentador or Reintentador()
        self.registro_costos = registro_costos or RegistroCostos(configuracion.tarifas)

    def consultar_modelo(
        self,
        pregunta: str,
        system_instruction: str | None = None,
        response_schema: dict[str, Any] | None = None,
    ) -> str:
        """Devuelve texto; el costo de la operación queda en registro_costos."""
        cuerpo = armar_peticion(pregunta, system_instruction, response_schema)
        try:
            respuesta = self._reintentador.ejecutar(lambda: self._transporte.enviar_peticion(cuerpo))
        except ErrorTemporal as error:
            raise ErrorServicioAgotado(
                "El servicio no respondió tras varios intentos. Intenta más tarde."
            ) from error

        # Se registra una sola vez por respuesta HTTP exitosa, fuera del reintento.
        self.registro_costos.registrar(respuesta)
        texto = extraer_texto(respuesta)
        if response_schema is not None:
            parsear_respuesta_json(texto, response_schema)
        return texto
