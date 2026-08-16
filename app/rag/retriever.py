from typing import TypedDict

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.embeddings import embed_text
from app.repositories.runbook_repository import RunbookRepository


class RetrievedRunbook(TypedDict):
    title: str
    source: str
    content: str


async def retrieve_runbooks(
    session: AsyncSession,
    query: str,
    limit: int = 3,
) -> list[RetrievedRunbook]:
    embedding = embed_text(query)
    repository = RunbookRepository(session)
    results = await repository.search(
        embedding,
        limit=limit,
    )
    return [
        {
            "title": item.title,
            "source": item.source,
            "content": item.content,
        }
        for item in results
    ]
