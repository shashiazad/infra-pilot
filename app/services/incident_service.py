import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.incident import Incident
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import IncidentCreate, IncidentUpdate


class IncidentService:

    def __init__(self, session: AsyncSession) -> None:
        self.repository = IncidentRepository(session)

    async def create_incident(
        self,
        data: IncidentCreate,
    ) -> Incident:

        incident = Incident(
            title=data.title,
            description=data.description,
            service=data.service,
            severity=data.severity,
        )

        return await self.repository.create(incident)

    async def get_incident(
        self,
        incident_id: uuid.UUID,
    ) -> Incident | None:

        return await self.repository.get_by_id(incident_id)

    async def get_incidents(self) -> list[Incident]:

        return await self.repository.get_all()

    async def update_incident(
        self,
        incident_id: uuid.UUID,
        data: IncidentUpdate,
    ) -> Incident | None:

        incident = await self.repository.get_by_id(
            incident_id
        )

        if incident is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(incident, field, value)

        await self.repository.session.commit()
        await self.repository.session.refresh(incident)

        return incident

    async def delete_incident(
        self,
        incident_id: uuid.UUID,
    ) -> bool:

        incident = await self.repository.get_by_id(
            incident_id
        )

        if incident is None:
            return False

        await self.repository.delete(incident)

        return True