from pydantic import BaseModel, Field


class IncidentClassification(BaseModel):
    category: str
    priority: str


class InvestigationResult(BaseModel):
    summary: str

    confirmed_facts: list[str] = Field(
        default_factory=list,
    )

    possible_causes: list[str] = Field(
        min_length=1,
    )

    recommended_checks: list[str] = Field(
        min_length=1,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
