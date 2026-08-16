import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.investigation import (
    ApprovalResponse,
    InvestigationDetailResponse,
    InvestigationListResponse,
    RemediationAuditResponse,
    RemediationExecutionResponse,
)
from app.services.investigation_service import (
    InvestigationService,
)

router = APIRouter(
    prefix="/investigations",
    tags=["Investigations"],
)


@router.get(
    "",
    response_model=list[InvestigationListResponse],
)
async def get_investigations(
    session: AsyncSession = Depends(get_db),
) -> list[InvestigationListResponse]:
    service = InvestigationService(session)
    return await service.get_investigations()


@router.get(
    "/remediations/audit",
    response_model=list[RemediationAuditResponse],
)
async def get_remediations(
    session: AsyncSession = Depends(get_db),
) -> list[RemediationAuditResponse]:
    service = InvestigationService(session)
    return await service.get_remediations()


@router.get(
    "/{run_id}",
    response_model=InvestigationDetailResponse,
)
async def get_investigation(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> InvestigationDetailResponse:

    service = InvestigationService(session)

    result = await service.get_investigation(
        run_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    return result


@router.post(
    "/{run_id}/approve",
    response_model=ApprovalResponse,
)
async def approve_investigation(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    service = InvestigationService(session)
    try:
        result = await service.approve_investigation(
            run_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )
    return result


@router.post(
    "/{run_id}/reject",
    response_model=ApprovalResponse,
)
async def reject_investigation(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    service = InvestigationService(session)
    try:
        result = await service.reject_investigation(
            run_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )
    return result


@router.post(
    "/{run_id}/execute",
    response_model=RemediationExecutionResponse,
)
async def execute_approved_remediation(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> RemediationExecutionResponse:
    service = InvestigationService(session)
    try:
        result = await (
            service.execute_approved_remediation(
                run_id
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )
    return result
