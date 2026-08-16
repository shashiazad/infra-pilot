from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.runbook import RunbookChunk


class RunbookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(
        self,
        embedding: list[float],
        limit: int = 3,
    ) -> list[RunbookChunk]:
        result = await self.session.execute(
            select(RunbookChunk)
            .order_by(
                RunbookChunk.embedding.cosine_distance(
                    embedding
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[RunbookChunk]:
        result = await self.session.execute(
            select(RunbookChunk).order_by(
                RunbookChunk.title.asc(),
                RunbookChunk.created_at.asc(),
            )
        )
        return list(result.scalars().all())
