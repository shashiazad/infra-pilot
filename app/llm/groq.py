from groq import RateLimitError
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.core.config import settings


def create_groq_model(
    model_name: str | None = None,
) -> ChatGroq:
    return ChatGroq(
        model=model_name or settings.llm_model,
        api_key=settings.groq_api_key,
        temperature=0,
    )


def create_structured_groq_model[T: BaseModel](
    schema: type[T],
):
    primary = create_groq_model().with_structured_output(
        schema,
        method="json_schema",
        strict=True,
    )
    fallback = create_groq_model(
        settings.llm_fallback_model
    ).with_structured_output(
        schema,
        method="json_schema",
        strict=True,
    )
    return primary.with_fallbacks(
        [fallback],
        exceptions_to_handle=(RateLimitError,),
    )


def create_tool_groq_model(
    tools: list[BaseTool],
):
    primary = create_groq_model().bind_tools(tools)
    fallback = create_groq_model(
        settings.llm_fallback_model
    ).bind_tools(tools)
    return primary.with_fallbacks(
        [fallback],
        exceptions_to_handle=(RateLimitError,),
    )
