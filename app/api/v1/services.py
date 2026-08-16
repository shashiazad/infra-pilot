from fastapi import APIRouter, HTTPException, Query, status

from app.core.config import settings
from app.schemas.service import ServiceSnapshot
from app.services.service_inventory_service import ServiceInventoryService

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=list[ServiceSnapshot])
async def get_services(
    namespace: str = Query(
        default=settings.kubernetes_namespace,
        min_length=1,
        max_length=253,
    ),
) -> list[ServiceSnapshot]:
    service = ServiceInventoryService()
    try:
        snapshots = await service.list_services(namespace)
        return await service.add_application_metrics(snapshots)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Kubernetes inventory unavailable: {exc}",
        ) from exc
