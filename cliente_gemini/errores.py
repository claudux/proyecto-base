"""Errores públicos que permiten reaccionar según la causa del fallo."""


class ErrorAutenticacion(ValueError):
    """La credencial o sus permisos requieren una corrección humana."""


class ErrorTemporal(TimeoutError):
    """Fallo que admite un nuevo intento tras una espera."""

    def __init__(self, mensaje: str, *, retry_after: float | None = None) -> None:
        super().__init__(mensaje)
        self.retry_after = retry_after


class ErrorProveedor(RuntimeError):
    """Respuesta inválida o fallo HTTP que no conviene repetir automáticamente."""


class ErrorServicioAgotado(RuntimeError):
    """El cliente agotó los intentos permitidos para un fallo temporal."""
