"""Unidad 2.6: dataset ficticio para clasificar preguntas académicas.

Prepara 15 pares y comprueba su validez localmente. No llama a Gemini ni entrena.
La salida JSON es el contrato del dataset; el clasificador actual de la Unidad
2.3 todavía espera una palabra y requeriría adaptación para usar un modelo afinado.
"""

import json
from collections import Counter

from google.genai import types


CATEGORIAS = frozenset({"indicador", "definicion", "sin_datos"})

# Las etiquetas describen la intención de la pregunta, no si el dato existe.
# Todas las preguntas son ficticias y no contienen información personal.
EJEMPLOS_RAW: list[tuple[str, dict[str, str]]] = [
    ("¿Cuántos estudiantes aprobaron el semestre anterior?", {"categoria": "indicador"}),
    ("¿Qué porcentaje de asistencia registró el programa de ejemplo?", {"categoria": "indicador"}),
    ("¿En cuántos puntos porcentuales cambió la retención entre dos períodos?",
     {"categoria": "indicador"}),
    ("Compara las tasas de deserción de los programas A y B.", {"categoria": "indicador"}),
    ("¿Cuál fue la tasa de aprobación en 2026, aunque la ficha no incluya ese año?",
     {"categoria": "indicador"}),
    ("¿Qué significa tasa de retención en el glosario académico?",
     {"categoria": "definicion"}),
    ("Explícame cómo se define la deserción estudiantil.", {"categoria": "definicion"}),
    ("¿Qué se entiende por estudiante evaluado en este indicador?",
     {"categoria": "definicion"}),
    ("¿Qué casos excluye la definición de aprobación académica?",
     {"categoria": "definicion"}),
    ("Define el concepto de período académico utilizado en la ficha.",
     {"categoria": "definicion"}),
    ("¿Cómo preparo una receta de pan casero?", {"categoria": "sin_datos"}),
    ("Recomiéndame una película para el fin de semana.", {"categoria": "sin_datos"}),
    ("¿Cuál es el pronóstico del tiempo para mañana?", {"categoria": "sin_datos"}),
    ("Escribe un poema sobre el mar.", {"categoria": "sin_datos"}),
    ("¿Quién ganó el último partido de fútbol?", {"categoria": "sin_datos"}),
]


def construir_ejemplos(
    pares: list[tuple[str, dict[str, str]]],
) -> list[types.TuningExample]:
    return [
        types.TuningExample(
            text_input=pregunta,
            output=json.dumps(salida, ensure_ascii=False, sort_keys=True),
        )
        for pregunta, salida in pares
    ]


def chequear_balance(
    pares: list[tuple[str, dict[str, str]]],
) -> Counter[str]:
    return Counter(salida["categoria"] for _, salida in pares)


def validar_dataset(ejemplos: list[types.TuningExample]) -> list[str]:
    """Valida el contrato exacto y detecta duplicados tras normalizar texto."""
    problemas: list[str] = []
    vistos: set[str] = set()
    for indice, ejemplo in enumerate(ejemplos):
        pregunta = ejemplo.text_input or ""
        salida_texto = ejemplo.output or ""
        if not pregunta.strip():
            problemas.append(f"ejemplo {indice}: text_input vacío")
        normalizada = " ".join(pregunta.casefold().split())
        if normalizada in vistos:
            problemas.append(f"ejemplo {indice}: text_input duplicado")
        vistos.add(normalizada)
        if not salida_texto.strip():
            problemas.append(f"ejemplo {indice}: output vacío")
            continue
        try:
            salida = json.loads(salida_texto)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {indice}: output no es JSON válido")
            continue
        if not isinstance(salida, dict) or set(salida) != {"categoria"}:
            problemas.append(f'ejemplo {indice}: output debe tener solo la clave "categoria"')
            continue
        if not isinstance(salida["categoria"], str) or salida["categoria"] not in CATEGORIAS:
            problemas.append(f"ejemplo {indice}: categoría no permitida")
    return problemas


def comprobar_pruebas_negativas(ejemplos: list[types.TuningExample]) -> None:
    """Demuestra dos fallos distintos sin contaminar los 15 pares de entrenamiento."""
    casos = (
        ("clave faltante", types.TuningExample(
            text_input="Pregunta rota de prueba", output="{}"
        ), 'output debe tener solo la clave "categoria"'),
        ("entrada duplicada", types.TuningExample(
            text_input=f"  {ejemplos[0].text_input.upper()}  ",
            output=ejemplos[0].output,
        ), "text_input duplicado"),
    )
    for nombre, roto, mensaje_esperado in casos:
        problemas = validar_dataset([*ejemplos, roto])
        if not any(mensaje_esperado in problema for problema in problemas):
            raise AssertionError(f"El validador no detectó: {nombre}")
        print(f"Prueba rota ({nombre}): detectada")
        for problema in problemas:
            print(f"  - {problema}")


def main() -> None:
    ejemplos = construir_ejemplos(EJEMPLOS_RAW)
    print("Unidad 2.6 — proyecto personal: clasificador académico")
    print(f"Pares válidos: {len(ejemplos)}")
    print("Balance por categoría:")
    for categoria, cantidad in sorted(chequear_balance(EJEMPLOS_RAW).items()):
        print(f"  {categoria}: {cantidad}")
    problemas = validar_dataset(ejemplos)
    print(f"Validación del dataset: {len(problemas)} problemas")
    if len(ejemplos) != 15 or problemas:
        raise SystemExit("El dataset académico no está listo.")
    comprobar_pruebas_negativas(ejemplos)
    print("Resultado: 15 pares válidos y 2 pruebas rotas detectadas.")


if __name__ == "__main__":
    main()
