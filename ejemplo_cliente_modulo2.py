"""Consulta manual optativa; las pruebas automáticas nunca usan la red."""

from cliente_gemini import ClienteGemini, Configuracion


def main() -> None:
    cliente = ClienteGemini(Configuracion.desde_entorno())
    texto = cliente.consultar_modelo(
        "Con estos datos ficticios, ¿cuántos puntos porcentuales cambió la "
        "tasa de aprobación de 68 % en 2024 a 74 % en 2025? "
        "Indica que la fuente es la Ficha académica ficticia A."
    )
    print(texto)
    operacion = cliente.registro_costos.ultima_operacion
    if operacion is not None:
        print(f"Costo estimado de la operación: USD {operacion.usd_estimados:.8f}")
    print(f"Costo estimado de la sesión: USD {cliente.registro_costos.costo_total_sesion:.8f}")


if __name__ == "__main__":
    main()
