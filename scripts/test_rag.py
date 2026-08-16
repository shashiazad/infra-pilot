import asyncio

from app.db.session import AsyncSessionLocal
from app.rag.retriever import retrieve_runbooks


async def main() -> None:
    async with AsyncSessionLocal() as session:
        results = await retrieve_runbooks(
            session,
            """
            payment service containers restart
            because database connections timeout
            """,
        )

        for result in results:
            print("\n", result["title"])


if __name__ == "__main__":
    asyncio.run(main())
