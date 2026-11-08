"""Modelo determinista para probar el ciclo del agente sin llamar a Gemini.

La selección en este modelo es programada. No constituye evidencia de que Gemini
elegirá las mismas herramientas; esa verificación se hace con --real.
"""

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class ModeloAgenteSimulado(BaseChatModel):
    def bind_tools(self, tools, **kwargs):
        return self.bind(tools=tools, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "agente_academico_simulado"

    def _generate(self, messages: list, stop: list[str] | None = None, **kwargs: Any) -> ChatResult:
        preguntas = [str(m.content) for m in messages if isinstance(m, HumanMessage)]
        pregunta = preguntas[-1] if preguntas else ""
        observaciones = [m for m in messages if isinstance(m, ToolMessage)]
        pregunta_normalizada = str(pregunta).lower()

        if not observaciones:
            if "qué significa" in pregunta_normalizada or "definición" in pregunta_normalizada:
                nombre, args = "consultar_definicion", {"indicador": "retención"}
            elif "cuánto aumentó" in pregunta_normalizada:
                nombre, args = "calcular_variacion", {
                    "indicador": "aprobación", "periodo_inicial": 2024, "periodo_final": 2025
                }
            elif "tasa de aprobación" in pregunta_normalizada:
                periodo = 2024 if "2024" in pregunta_normalizada else 2025
                nombre, args = "consultar_indicador", {"indicador": "aprobación", "periodo": periodo}
            elif "y en 2024" in pregunta_normalizada and any(
                "tasa de aprobación" in anterior.lower() for anterior in preguntas[:-1]
            ):
                nombre, args = "consultar_indicador", {"indicador": "aprobación", "periodo": 2024}
            else:
                respuesta = "No hay información suficiente en el catálogo ficticio para responder."
                return ChatResult(generations=[ChatGeneration(message=AIMessage(content=respuesta))])
            mensaje = AIMessage(content="", tool_calls=[{"name": nombre, "args": args, "id": "paso-1"}])
        elif "qué ficha" in pregunta_normalizada and len(observaciones) == 1:
            mensaje = AIMessage(content="", tool_calls=[{
                "name": "consultar_fuente", "args": {"fuente_id": "FICHA-A"}, "id": "paso-2"
            }])
        else:
            respuesta = " ".join(str(m.content) for m in observaciones)
            mensaje = AIMessage(content=respuesta)
        return ChatResult(generations=[ChatGeneration(message=mensaje)])
