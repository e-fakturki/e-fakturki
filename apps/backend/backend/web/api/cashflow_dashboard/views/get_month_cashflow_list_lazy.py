from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.repositories.cashflow_dashboard_repository import (
    get_cashflow_list_lazy,
)
from backend.db.repositories.company_repository import get_company_nip
from backend.db.dependencies import get_db_session
from backend.schemas.auth import UserRead
from backend.web.api.auth.services import get_current_user

from backend.schemas.cashflow_dashboard import CASHFLOW_TYPE, SORT_CASHFLOW_LIST_BY, SORT_ORDER, CashflowListItem

router = APIRouter()


@router.get("/month-cashflow-list", status_code=200, response_model=list[CashflowListItem])
async def get_month_cashflow_list(
    company_id: str = Query(..., description="The ID of the company to filter by."),
    year: int = Query(..., description="The year to filter by."),
    month: int = Query(..., description="The month to filter by."),
    type: CASHFLOW_TYPE | None = Query(None, description="The type of cashflow to filter by."),
    offset: int = Query(0, description="The offset for pagination."),
    limit: int = Query(50, description="The limit for pagination."),
    sort_by: SORT_CASHFLOW_LIST_BY | None = Query(None, description="The field to sort by."),
    sort_order: SORT_ORDER | None = Query(None, description="The order to sort by (asc or desc)."),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[CashflowListItem]:
    """Get the list of sales/costs (right now only invoices) for the month for a company."""

    company_nip = await get_company_nip(db_session, company_id)

    try:
        return await get_cashflow_list_lazy(
            db=db_session, 
            company_nip=company_nip, 
            year=year,
            month=month,
            type=type,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
