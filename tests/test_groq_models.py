from groq import BadRequestError, RateLimitError

from app.llm import groq
from app.schemas.investigation import InvestigationResult


class FakeModel:
    def __init__(self, name: str) -> None:
        self.name = name
        self.structured_kwargs: dict = {}
        self.fallbacks: list[FakeModel] = []
        self.exceptions: tuple[type[Exception], ...] = ()

    def with_structured_output(self, schema, **kwargs):
        self.structured_kwargs = kwargs
        return self

    def with_fallbacks(
        self,
        fallbacks,
        exceptions_to_handle,
    ):
        self.fallbacks = fallbacks
        self.exceptions = exceptions_to_handle
        return self


def test_structured_models_use_gpt_oss_configuration(
    monkeypatch,
) -> None:
    created: list[FakeModel] = []

    def fake_create(model_name=None):
        model = FakeModel(model_name)
        created.append(model)
        return model

    monkeypatch.setattr(
        groq,
        "create_groq_model",
        fake_create,
    )
    monkeypatch.setattr(
        groq.settings,
        "llm_structured_model",
        "openai/gpt-oss-120b",
    )
    monkeypatch.setattr(
        groq.settings,
        "llm_structured_fallback_model",
        "openai/gpt-oss-20b",
    )

    model = groq.create_structured_groq_model(InvestigationResult)

    assert [item.name for item in created] == [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
    ]
    assert created[0].structured_kwargs == {
        "method": "json_schema",
        "strict": True,
    }
    assert model.fallbacks == [created[1]]
    assert model.exceptions == (
        RateLimitError,
        BadRequestError,
    )
