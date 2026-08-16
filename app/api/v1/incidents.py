import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
)
from app.schemas.investigation import InvestigationResult
from app.services.incident_service import IncidentService
from app.services.investigation_service import InvestigationService

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
    data: IncidentCreate,
    session: AsyncSession = Depends(get_db),
) -> IncidentResponse:

    service = IncidentService(session)

    return await service.create_incident(data)


@router.get(
    "",
    response_model=list[IncidentResponse],
)
async def get_incidents(
    session: AsyncSession = Depends(get_db),
) -> list[IncidentResponse]:

    service = IncidentService(session)

    return await service.get_incidents()


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def get_incident(
    incident_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> IncidentResponse:

    service = IncidentService(session)

    incident = await service.get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def update_incident(
    incident_id: uuid.UUID,
    data: IncidentUpdate,
    session: AsyncSession = Depends(get_db),
) -> IncidentResponse:

    service = IncidentService(session)

    incident = await service.update_incident(
        incident_id,
        data,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_incident(
    incident_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> None:

    service = IncidentService(session)

    deleted = await service.delete_incident(incident_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )


@router.post(
    "/{incident_id}/investigate",
    response_model=InvestigationResult,
)
async def investigate_incident(
    incident_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> InvestigationResult:

    repository = IncidentRepository(session)

    service = InvestigationService()

    result = await service.investigate(
        incident_id,
        repository,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return result
