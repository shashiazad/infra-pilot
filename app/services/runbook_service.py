from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.retriever import retrieve_runbooks
from app.schemas.runbook import RunbookResult


class RunbookService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def retrieve(
        self,
        query: str,
        limit: int = 3,
    ) -> list[RunbookResult]:
        results = await retrieve_runbooks(
            session=self.session,
            query=query,
            limit=limit,
        )
        return [RunbookResult.model_validate(item) for item in results]
