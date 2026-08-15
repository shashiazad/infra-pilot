import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=1)
    service: str = Field(min_length=1, max_length=100)
    severity: str = Field(min_length=1, max_length=20)


class IncidentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )
    description: str | None = None
    service: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    severity: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )
    status: str | None = Field(
        default=None,
        max_length=30,
    )


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    service: str
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime