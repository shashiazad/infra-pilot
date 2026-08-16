import uuid
from datetime import datetime
from typing import Any

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


class RemediationProposal(BaseModel):
    action: str
    reason: str
    target_service: str
    risk: str
    commands: list[str] = Field(
        default_factory=list,
    )
    requires_approval: bool = True


class InvestigationRunResponse(BaseModel):
    run_id: uuid.UUID

    status: str

    classification: dict[str, Any]

    investigation_plan: list[str]

    evidence: list[dict[str, Any]]

    analysis: InvestigationResult

    remediation_proposal: RemediationProposal

    approval_status: str | None
    remediation_status: str | None

    tool_iterations: int

class InvestigationEvidenceResponse(BaseModel):
    tool: str
    status: str
    finding: dict[str, Any] | str
    created_at: datetime


class InvestigationDetailResponse(BaseModel):
    run_id: uuid.UUID
    incident_id: uuid.UUID

    status: str

    classification: dict[str, Any] | None
    investigation_plan: list[str] | None
    analysis: dict[str, Any] | None
    remediation_proposal: dict[str, Any] | None
    approval_status: str | None
    remediation_status: str | None
    remediation_result: dict[str, Any] | None

    tool_iterations: int

    evidence: list[InvestigationEvidenceResponse]

    started_at: datetime
    completed_at: datetime | None

class InvestigationSummaryResponse(BaseModel):
    run_id: uuid.UUID
    incident_id: uuid.UUID
    status: str
    tool_iterations: int
    started_at: datetime
    completed_at: datetime | None


class ApprovalResponse(BaseModel):
    run_id: uuid.UUID
    approval_status: str
    remediation_status: str | None


class RemediationExecutionResponse(BaseModel):
    run_id: uuid.UUID
    approval_status: str
    remediation_status: str
    remediation_result: dict[str, Any] | None
