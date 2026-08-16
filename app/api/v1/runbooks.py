from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.runbook import RunbookCatalogResponse
from app.services.runbook_service import RunbookService

router = APIRouter(prefix="/runbooks", tags=["Runbooks"])


@router.get("", response_model=list[RunbookCatalogResponse])
async def get_runbooks(
    session: AsyncSession = Depends(get_db),
) -> list[RunbookCatalogResponse]:
    return await RunbookService(session).catalog()
