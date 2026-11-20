"""Unidad 2.6: ejemplo didáctico de clasificación de tickets de soporte.

Prepara 15 pares para inspección local. No crea trabajos de tuning ni usa red.
"""

import json
from collections import Counter

from google.genai import types


INTENCIONES = frozenset(
    {"acceso", "facturacion", "consulta_plan", "falla_tecnica", "cancelacion"}
)
PRIORIDADES = frozenset({"alta", "media", "baja"})
CLAVES = frozenset({"intencion", "prioridad"})

# Casos ficticios. La prioridad es una etiqueta didáctica, no una política real.
EJEMPLOS_RAW: list[tuple[str, dict[str, str]]] = [
    ("No puedo entrar a mi cuenta y necesito entregar un trabajo hoy.",
     {"intencion": "acceso", "prioridad": "alta"}),
    ("No recibo el enlace para restablecer mi contraseña.",
     {"intencion": "acceso", "prioridad": "media"}),
    ("Quisiera cambiar mi contraseña por prevención, sin urgencia.",
     {"intencion": "acceso", "prioridad": "baja"}),
    ("Me cobraron dos veces este mes; necesito revisar el cargo hoy.",
     {"intencion": "facturacion", "prioridad": "alta"}),
    ("La factura del último pago no aparece en mi cuenta.",
     {"intencion": "facturacion", "prioridad": "media"}),
    ("¿En qué fecha se emitirá el próximo cobro de mi plan?",
     {"intencion": "facturacion", "prioridad": "baja"}),
    ("¿Cuántas personas pueden usar el plan Pro? No es urgente.",
     {"intencion": "consulta_plan", "prioridad": "baja"}),
    ("Quiero comparar las funciones de los planes Básico y Pro.",
     {"intencion": "consulta_plan", "prioridad": "baja"}),
    ("¿El plan de equipo permite más espacio de almacenamiento?",
     {"intencion": "consulta_plan", "prioridad": "baja"}),
    ("La aplicación se cierra al guardar y perderé el trabajo de hoy.",
     {"intencion": "falla_tecnica", "prioridad": "alta"}),
    ("No se completa la carga de un archivo PDF en la aplicación.",
     {"intencion": "falla_tecnica", "prioridad": "media"}),
    ("Las notificaciones llegan con demora, pero la aplicación funciona.",
     {"intencion": "falla_tecnica", "prioridad": "baja"}),
    ("Necesito cancelar la renovación automática antes del cobro de hoy.",
     {"intencion": "cancelacion", "prioridad": "alta"}),
    ("Quiero dar de baja mi cuenta al terminar el período actual.",
     {"intencion": "cancelacion", "prioridad": "media"}),
    ("¿Cómo cancelo mi plan el próximo mes? Solo busco el procedimiento.",
     {"intencion": "cancelacion", "prioridad": "baja"}),
]


def construir_ejemplos(
    pares: list[tuple[str, dict[str, str]]],
) -> list[types.TuningExample]:
    return [
        types.TuningExample(
            text_input=texto,
            output=json.dumps(salida, ensure_ascii=False, sort_keys=True),
        )
        for texto, salida in pares
    ]


def chequear_balance(
    pares: list[tuple[str, dict[str, str]]],
) -> Counter[str]:
    return Counter(salida["intencion"] for _, salida in pares)


def validar_dataset(ejemplos: list[types.TuningExample]) -> list[str]:
    """Comprueba formato, etiquetas y entradas repetidas antes de entrenar."""
    problemas: list[str] = []
    vistos: set[str] = set()
    for indice, ejemplo in enumerate(ejemplos):
        texto = ejemplo.text_input or ""
        salida_texto = ejemplo.output or ""
        if not texto.strip():
            problemas.append(f"ejemplo {indice}: text_input vacío")
        normalizado = " ".join(texto.casefold().split())
        if normalizado in vistos:
            problemas.append(f"ejemplo {indice}: text_input duplicado")
        vistos.add(normalizado)
        if not salida_texto.strip():
            problemas.append(f"ejemplo {indice}: output vacío")
            continue
        try:
            salida = json.loads(salida_texto)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {indice}: output no es JSON válido")
            continue
        if not isinstance(salida, dict) or set(salida) != CLAVES:
            problemas.append(f"ejemplo {indice}: output debe tener exactamente {sorted(CLAVES)}")
            continue
        if not isinstance(salida["intencion"], str) or salida["intencion"] not in INTENCIONES:
            problemas.append(f"ejemplo {indice}: intención no permitida")
        if not isinstance(salida["prioridad"], str) or salida["prioridad"] not in PRIORIDADES:
            problemas.append(f"ejemplo {indice}: prioridad no permitida")
    return problemas


def comprobar_pruebas_negativas(ejemplos: list[types.TuningExample]) -> None:
    """Dos pares rotos independientes; nunca se incluyen en el dataset válido."""
    casos = (
        ("JSON inválido", types.TuningExample(text_input="Caso roto de prueba", output="{mal json"),
         "output no es JSON válido"),
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
    print("Unidad 2.6 — ejercicio propuesto: tickets de soporte")
    print(f"Pares válidos: {len(ejemplos)}")
    print("Balance por intención:")
    for intencion, cantidad in sorted(chequear_balance(EJEMPLOS_RAW).items()):
        print(f"  {intencion}: {cantidad}")
    problemas = validar_dataset(ejemplos)
    print(f"Validación del dataset: {len(problemas)} problemas")
    if len(ejemplos) != 15 or problemas:
        raise SystemExit("El dataset didáctico no está listo.")
    comprobar_pruebas_negativas(ejemplos)
    print("Resultado: 15 pares válidos y 2 pruebas rotas detectadas.")


if __name__ == "__main__":
    main()
