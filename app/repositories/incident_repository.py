import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.incident import Incident


class IncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, incident: Incident) -> Incident:
        self.session.add(incident)

        await self.session.commit()
        await self.session.refresh(incident)

        return incident

    async def get_by_id(
        self,
        incident_id: uuid.UUID,
    ) -> Incident | None:

        result = await self.session.execute(
            select(Incident).where(Incident.id == incident_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Incident]:

        result = await self.session.execute(
            select(Incident).order_by(Incident.created_at.desc())
        )

        return list(result.scalars().all())

    async def delete(self, incident: Incident) -> None:
        await self.session.delete(incident)
        await self.session.commit()
