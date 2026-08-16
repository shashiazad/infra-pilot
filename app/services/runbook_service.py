from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.retriever import retrieve_runbooks
from app.repositories.runbook_repository import RunbookRepository
from app.schemas.runbook import RunbookCatalogResponse, RunbookResult


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

    async def catalog(self) -> list[RunbookCatalogResponse]:
        chunks = await RunbookRepository(self.session).get_all()
        grouped: dict[tuple[str, str], list] = {}
        for chunk in chunks:
            grouped.setdefault((chunk.title, chunk.source), []).append(chunk)
        return [
            RunbookCatalogResponse(
                title=title,
                source=source,
                chunks=len(items),
                last_indexed=max(item.created_at for item in items),
                content="\n\n".join(item.content for item in items),
            )
            for (title, source), items in grouped.items()
        ]
