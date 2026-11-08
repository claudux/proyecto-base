"""Catálogo pequeño y coherente para la demostración del agente.

Todos los registros son ficticios. Esta estructura puede reemplazarse por una
fuente autorizada en una etapa posterior sin cambiar el contrato de las herramientas.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Indicador:
    nombre: str
    definicion: str
    fuente_id: str
    valores: dict[int, int]


FUENTES = {
    "FICHA-A": "Ficha académica ficticia A: indicadores anuales 2024 y 2025.",
    "REG-B": "Registro ficticio de asistencia B: períodos 2024 y 2025.",
    "FICHA-C": "Ficha académica ficticia C: retención 2024 y 2025.",
}

INDICADORES = {
    "aprobacion": Indicador(
        "tasa de aprobación",
        "Porcentaje de estudiantes aprobados sobre estudiantes evaluados; excluye convalidaciones.",
        "FICHA-A",
        {2024: 68, 2025: 74},
    ),
    "asistencia": Indicador(
        "tasa de asistencia",
        "Porcentaje de asistencias registradas sobre sesiones programadas.",
        "REG-B",
        {2024: 82, 2025: 85},
    ),
    "retencion": Indicador(
        "tasa de retención",
        "Porcentaje de estudiantes que continúan matriculados al período siguiente.",
        "FICHA-C",
        {2024: 90, 2025: 92},
    ),
}
