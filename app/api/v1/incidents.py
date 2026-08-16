import uuid
from collections.abc import AsyncIterable

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.sse import (
    EventSourceResponse,
    ServerSentEvent,
)
from groq import RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
)
from app.schemas.investigation import (
    InvestigationRunResponse,
    InvestigationSummaryResponse,
)
from app.services.incident_service import IncidentService
from app.services.investigation_service import InvestigationService

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


# -------------------------------------------------------------------
# CREATE INCIDENT
# -------------------------------------------------------------------

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


# -------------------------------------------------------------------
# GET ALL INCIDENTS
# -------------------------------------------------------------------

@router.get(
    "",
    response_model=list[IncidentResponse],
)
async def get_incidents(
    session: AsyncSession = Depends(get_db),
) -> list[IncidentResponse]:

    service = IncidentService(session)

    return await service.get_incidents()


# -------------------------------------------------------------------
# GET INCIDENT BY ID
# -------------------------------------------------------------------

@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def get_incident(
    incident_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> IncidentResponse:

    service = IncidentService(session)

    incident = await service.get_incident(
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident


# -------------------------------------------------------------------
# UPDATE INCIDENT
# -------------------------------------------------------------------

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


# -------------------------------------------------------------------
# DELETE INCIDENT
# -------------------------------------------------------------------

@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_incident(
    incident_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> None:

    service = IncidentService(session)

    deleted = await service.delete_incident(
        incident_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )


# -------------------------------------------------------------------
# RUN INVESTIGATION
# -------------------------------------------------------------------

@router.post(
    "/{incident_id}/investigate",
    response_model=InvestigationRunResponse,
)
async def investigate_incident(
    incident_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> InvestigationRunResponse:

    service = InvestigationService(
        session
    )

    try:
        result = await service.investigate(
            incident_id
        )
    except RateLimitError as exc:
        retry_after = exc.response.headers.get(
            "retry-after"
        )
        retry_message = (
            f" Retry after {retry_after} seconds."
            if retry_after
            else " Please retry after the provider quota resets."
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "The investigation model is temporarily rate limited."
                + retry_message
            ),
            headers=(
                {"Retry-After": retry_after}
                if retry_after
                else None
            ),
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return result


# -------------------------------------------------------------------
# STREAM INVESTIGATION USING SSE
# -------------------------------------------------------------------

@router.post(
    "/{incident_id}/investigate/stream",
    response_class=EventSourceResponse,
)
async def stream_incident_investigation(
    incident_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> AsyncIterable[ServerSentEvent]:

    service = InvestigationService(
        session
    )

    async for event in service.stream_investigation(
        incident_id
    ):
        yield ServerSentEvent(
            event=event["event"],
            data=event["data"],
        )


# -------------------------------------------------------------------
# GET INVESTIGATION HISTORY FOR INCIDENT
# -------------------------------------------------------------------

@router.get(
    "/{incident_id}/investigations",
    response_model=list[InvestigationSummaryResponse],
)
async def get_incident_investigations(
    incident_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> list[InvestigationSummaryResponse]:

    incident_service = IncidentService(
        session
    )

    incident = await incident_service.get_incident(
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    investigation_service = InvestigationService(
        session
    )

    return await (
        investigation_service
        .get_incident_investigations(
            incident_id
        )
    )
