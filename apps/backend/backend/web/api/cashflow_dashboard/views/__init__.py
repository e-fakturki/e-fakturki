from fastapi import APIRouter

from .get_monthly_profits import router as get_monthly_profits_router

router = APIRouter(prefix="/cashflow", tags=["cashflow"])

router.include_router(get_monthly_profits_router)
