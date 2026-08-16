from typing import TypeVar

from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


def create_groq_model() -> ChatGroq:
    return ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        temperature=0,
    )


def create_structured_groq_model(
    schema: type[T],
) -> ChatGroq:
    model = create_groq_model()

    return model.with_structured_output(schema)
