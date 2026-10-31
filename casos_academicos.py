"""Veinte casos académicos sencillos con datos y fuentes ficticios.

Las referencias se escribieron antes de generar respuestas. Ninguna cifra
representa a una institución ni procede de una fuente real.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CasoAcademico:
    id: str
    pregunta: str
    contexto: str
    referencia: str
    fuente: str


def _caso(
    numero: int, pregunta: str, dato: str, respuesta_esperada: str, fuente: str
) -> CasoAcademico:
    return CasoAcademico(
        id=f"A{numero:02d}",
        pregunta=pregunta,
        contexto=f"Fuente: {fuente}. {dato}",
        referencia=f"{respuesta_esperada} Fuente: {fuente}.",
        fuente=fuente,
    )


CASOS: tuple[CasoAcademico, ...] = (
    _caso(1, "¿Cuál fue la tasa de aprobación en 2024?",
          "La tasa de aprobación de 2024 fue 68 %.",
          "La tasa de aprobación en 2024 fue 68 %.", "Ficha académica ficticia A"),
    _caso(2, "¿Cuál fue la tasa de aprobación en 2025?",
          "La tasa de aprobación de 2025 fue 74 %.",
          "La tasa de aprobación en 2025 fue 74 %.", "Ficha académica ficticia A"),
    _caso(3, "¿Cuántos puntos porcentuales subió la aprobación de 2024 a 2025?",
          "Aprobación: 68 % en 2024 y 74 % en 2025.",
          "La aprobación subió 6 puntos porcentuales de 2024 a 2025.",
          "Ficha académica ficticia A"),
    _caso(4, "¿En cuál de los dos años fue mayor la aprobación?",
          "Aprobación: 68 % en 2024 y 74 % en 2025.",
          "La aprobación fue mayor en 2025, con 74 %.",
          "Ficha académica ficticia A"),
    _caso(5, "Si aprobaron 74 de 100 estudiantes, ¿cuál es la tasa?",
          "En 2025 aprobaron 74 de 100 estudiantes evaluados.",
          "La tasa de aprobación de 2025 fue 74 %.",
          "Ficha académica ficticia A"),
    _caso(6, "¿Cuál fue la asistencia en 2024?",
          "La tasa de asistencia fue 82 % en 2024.",
          "La asistencia de 2024 fue 82 %.", "Registro ficticio de asistencia B"),
    _caso(7, "¿Cuál fue la asistencia en 2025?",
          "La tasa de asistencia fue 85 % en 2025.",
          "La asistencia de 2025 fue 85 %.", "Registro ficticio de asistencia B"),
    _caso(8, "¿Cuánto cambió la asistencia entre 2024 y 2025?",
          "Asistencia: 82 % en 2024 y 85 % en 2025.",
          "La asistencia aumentó 3 puntos porcentuales entre 2024 y 2025.",
          "Registro ficticio de asistencia B"),
    _caso(9, "¿Cuánto cambió la retención entre 2024 y 2025?",
          "Retención: 90 % en 2024 y 92 % en 2025.",
          "La retención aumentó 2 puntos porcentuales entre 2024 y 2025.",
          "Ficha académica ficticia C"),
    _caso(10, "¿Qué significa retención en esta ficha?",
          "Retención: proporción de estudiantes que continúan matriculados al período siguiente.",
          "La retención es la proporción de estudiantes que continúan matriculados al período siguiente.",
          "Ficha académica ficticia C"),
    _caso(11, "¿Cuánto bajó la deserción entre 2024 y 2025?",
          "Deserción: 12 % en 2024 y 9 % en 2025.",
          "La deserción bajó 3 puntos porcentuales entre 2024 y 2025.",
          "Ficha académica ficticia C"),
    _caso(12, "¿Qué programa tuvo mayor aprobación, A o B?",
          "Aprobación del programa A: 70 %. Aprobación del programa B: 65 %.",
          "El programa A tuvo mayor aprobación, con 70 %.",
          "Comparación ficticia de programas D"),
    _caso(13, "¿Cuántos puntos separan las tasas de aprobación de A y B?",
          "Aprobación del programa A: 70 %. Aprobación del programa B: 65 %.",
          "Las tasas de aprobación de A y B difieren en 5 puntos porcentuales.",
          "Comparación ficticia de programas D"),
    _caso(14, "¿Cuántos préstamos más registró la biblioteca en 2025?",
          "Préstamos de biblioteca: 120 en 2024 y 150 en 2025.",
          "La biblioteca registró 30 préstamos más en 2025 que en 2024.",
          "Registro ficticio de biblioteca E"),
    _caso(15, "Si se aprobaron 18 de 20 cursos, ¿qué porcentaje es?",
          "En el período de ejemplo se aprobaron 18 de 20 cursos.",
          "Se aprobó el 90 % de los cursos.", "Ficha académica ficticia F"),
    _caso(16, "Si 40 de 200 estudiantes obtuvieron beca, ¿qué porcentaje es?",
          "Obtuvieron beca 40 de 200 estudiantes del ejemplo.",
          "Obtuvo beca el 20 % de los estudiantes.",
          "Registro ficticio de becas G"),
    _caso(17, "¿Cuál es el puntaje mínimo para aprobar según esta ficha?",
          "La ficha establece un mínimo de 60 puntos sobre 100 para aprobar.",
          "El puntaje mínimo para aprobar es 60 sobre 100.",
          "Reglamento académico ficticio H"),
    _caso(18, "¿Cuál fue la edad promedio de los estudiantes?",
          "La ficha solo indica 100 estudiantes evaluados; no informa edades.",
          "No es posible determinar la edad promedio porque faltan datos de edad.",
          "Ficha académica ficticia A"),
    _caso(19, "¿Cuál fue la tasa de aprobación en 2026?",
          "La ficha informa 68 % en 2024 y 74 % en 2025; no incluye 2026.",
          "No es posible determinar la aprobación de 2026 porque ese dato no está informado.",
          "Ficha académica ficticia A"),
    _caso(20, "¿La tasa de aprobación incluye convalidaciones?",
          "La definición de la tasa de aprobación excluye las convalidaciones.",
          "No, la tasa de aprobación excluye las convalidaciones.",
          "Reglamento académico ficticio H"),
)
