"""Consulta manual optativa; las pruebas automáticas nunca usan la red."""

from cliente_gemini import ClienteGemini, Configuracion


def main() -> None:
    cliente = ClienteGemini(Configuracion.desde_entorno())
    texto = cliente.consultar_modelo("¿Qué es El Niño? Responde en dos oraciones.")
    print(texto)
    operacion = cliente.registro_costos.ultima_operacion
    if operacion is not None:
        print(f"Costo estimado de la operación: USD {operacion.usd_estimados:.8f}")
    print(f"Costo estimado de la sesión: USD {cliente.registro_costos.costo_total_sesion:.8f}")


if __name__ == "__main__":
    main()
