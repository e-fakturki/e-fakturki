from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.repositories.cashflow_dashboard.cashflow_per_contractor import (
    get_cashflow_per_contractor,
)
from backend.db.repositories.company_repository import get_company_nip
from backend.db.dependencies import get_db_session
from backend.schemas.auth import UserRead
from backend.web.api.auth.services import get_current_user

from backend.schemas.cashflow_dashboard import CASHFLOW_TYPE, ContractorCashflowItem

router = APIRouter()


@router.get(
    "/cashflow-per-contractor-distribution",
    status_code=200,
    response_model=list[ContractorCashflowItem],
)
async def get_cashflow_per_contractor_distribution(
    company_id: str = Query(..., description="The ID of the company to filter by."),
    year: int = Query(..., description="The year to filter by."),
    month: int = Query(..., description="The month to filter by."),
    cashflow_type: CASHFLOW_TYPE = Query(
        ..., description="The type of cashflow to filter by, either 'sales' or 'costs'."
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[ContractorCashflowItem]:
    """Get the cashflow per contractor for a company."""

    company_nip = await get_company_nip(db_session, company_id)

    try:
        return await get_cashflow_per_contractor(
            db=db_session,
            company_nip=company_nip,
            year=year,
            month=month,
            cashflow_type=cashflow_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
