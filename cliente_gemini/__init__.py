"""Cliente de Gemini del borrador local del módulo 2."""

from .cliente import ClienteGemini
from .configuracion import Configuracion, Tarifas
from .errores import ErrorAutenticacion, ErrorProveedor, ErrorServicioAgotado, ErrorTemporal

__all__ = [
    "ClienteGemini",
    "Configuracion",
    "Tarifas",
    "ErrorAutenticacion",
    "ErrorProveedor",
    "ErrorServicioAgotado",
    "ErrorTemporal",
]
