"""El conjunto de evaluación se mantiene simple, completo y ficticio."""

from casos_academicos import CASOS


def test_veinte_casos_distintos_con_referencia_y_fuente_ficticia():
    assert len(CASOS) == 20
    assert len({caso.id for caso in CASOS}) == 20
    assert all(caso.pregunta and caso.contexto and caso.referencia for caso in CASOS)
    assert all("fictici" in caso.fuente for caso in CASOS)
