from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.repositories.cashflow_dashboard_repository import (
    get_month_summary,
)
from backend.db.repositories.company_repository import get_company_nip
from backend.db.dependencies import get_db_session
from backend.schemas.auth import UserRead
from backend.web.api.auth.services import get_current_user

from backend.schemas.cashflow_dashboard import MonthlyProfitSummary

router = APIRouter()


@router.get("/monthly-sales-summary", status_code=200, response_model=MonthlyProfitSummary)
async def get_monthly_sales_summary(
    company_id: str = Query(..., description="The ID of the company to filter by."),
    year: int = Query(..., description="The year to filter by."),
    month: int = Query(..., description="The month to filter by."),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> MonthlyProfitSummary:
    """Get the monthly sales summary for a company."""

    company_nip = await get_company_nip(db_session, company_id)

    try:
        return await get_month_summary(
            db=db_session, company_nip=company_nip, year=year, month=month
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
