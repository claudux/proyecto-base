# Verificación técnica previa al Gate 1

**Fecha:** 23 de octubre de 2026  
**Sistema de prueba:** Windows, PowerShell, Python 3.14.6

## Comprobaciones realizadas

| Comprobación | Resultado |
| --- | --- |
| Instalación de `requirements.txt` en un entorno virtual nuevo, fuera del repositorio | Correcta; se instalaron `python-dotenv`, `requests` y sus dependencias transitivas. |
| `python -m pip check` en ese entorno | Sin dependencias incompatibles. |
| Importación de `requests` y `dotenv` en ese entorno | Correcta. |
| Ejecución de `python -m src.consumir_gemini` desde el proyecto con ese entorno | Respuesta real de Gemini, latencia y costo estimado; código de salida 0. |
| Ejecución sin `GEMINI_API_KEY` | Mensaje de error y código de salida 1. |
| `git check-ignore .env` y `git log --all --oneline -- .env` | `.env` está ignorado y no aparecen commits que lo rastreen. |

La instalación se probó con un entorno nuevo, pero ejecutando el código de la
copia de desarrollo. **Todavía falta el ensayo completo desde un clon nuevo del
repositorio remoto**, después de publicar las correcciones finales. El
procedimiento está en el README. No se guardó ninguna credencial en este archivo.
