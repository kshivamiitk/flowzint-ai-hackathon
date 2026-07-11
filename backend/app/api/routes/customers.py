from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_query_service
from app.application.dto import CustomerDTO, TransactionDTO
from app.application.query_service import QueryService

router = APIRouter(tags=["customers"])


@router.get("/customers", response_model=list[CustomerDTO])
async def list_customers(
    service: QueryService = Depends(get_query_service),
) -> list[CustomerDTO]:
    return await service.customers()


@router.get("/transactions", response_model=list[TransactionDTO])
async def list_transactions(
    customer_id: str | None = Query(default=None),
    service: QueryService = Depends(get_query_service),
) -> list[TransactionDTO]:
    return await service.transactions(customer_id)
