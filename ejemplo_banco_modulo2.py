"""Ejemplo optativo con el banco de prompts existente del Gate 1."""

from cliente_gemini import ClienteGemini, Configuracion
from prompts.banco import BANCO_DE_PROMPTS


def main() -> None:
    cliente = ClienteGemini(Configuracion.desde_entorno())
    prompt = BANCO_DE_PROMPTS[0]
    respuesta = cliente.consultar_modelo(
        prompt["ejemplo_usuario"],
        system_instruction=prompt["system_instruction"],
        response_schema=prompt["response_schema"],
    )
    print(respuesta)
    print(f"Costo estimado: USD {cliente.registro_costos.costo_total_sesion:.8f}")


if __name__ == "__main__":
    main()
