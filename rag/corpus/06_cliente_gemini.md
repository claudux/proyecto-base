# Cliente Gemini del prototipo

El cliente modular del proyecto envía peticiones a Gemini y registra los metadatos de uso recibidos. Ante errores temporales de red o servicio aplica reintentos limitados; los errores de autenticación no se reintentan. La clave API se obtiene del entorno y no debe guardarse en el corpus ni en los registros de evaluación.
