"""Ejecuta una vez cada prompt del ejercicio mediante el cliente del módulo 2.

Hace tres llamadas reales a Gemini y consume cuota. No modifica registros de Gate 1.
"""

from cliente_gemini import ClienteGemini, Configuracion
from prompts.banco import BANCO_DE_PROMPTS


def main() -> int:
    cliente = ClienteGemini(Configuracion.desde_entorno())
    fallos = 0

    for prompt in BANCO_DE_PROMPTS:
        try:
            texto = cliente.consultar_modelo(
                prompt["ejemplo_usuario"],
                system_instruction=prompt["system_instruction"],
                response_schema=prompt["response_schema"],
            )
        except (ValueError, RuntimeError) as error:
            fallos += 1
            print(f"{prompt['nombre']}: ERROR — {error}")
            continue

        operacion = cliente.registro_costos.ultima_operacion
        print(f"{prompt['nombre']}: {texto}")
        if operacion is not None:
            print(f"  Costo estimado: USD {operacion.usd_estimados:.8f}")

    print(f"Costo total estimado de la sesión: USD {cliente.registro_costos.costo_total_sesion:.8f}")
    print(f"Prompts completados: {len(BANCO_DE_PROMPTS) - fallos}/{len(BANCO_DE_PROMPTS)}")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
