import asyncio
from pathlib import Path

from sqlalchemy import delete

from app.db.models.runbook import RunbookChunk
from app.db.session import AsyncSessionLocal
from app.rag.embeddings import embed_text

RUNBOOK_DIR = Path(__file__).resolve().parents[1] / "runbooks"


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(delete(RunbookChunk))

        for path in sorted(RUNBOOK_DIR.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            session.add(
                RunbookChunk(
                    title=path.stem,
                    source=str(path.relative_to(RUNBOOK_DIR.parent)),
                    content=content,
                    embedding=embed_text(content),
                )
            )
            print("Indexed:", path.name)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
