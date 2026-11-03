from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Integer, cast, func, select

from backend.db.models.invoices_brief import InvoicesBriefTable
from backend.schemas.cashflow_dashboard import MontlyProfitItem


async def get_monthly_profit_list(
    db: AsyncSession,
    company_nip: str,
    year: int
) -> list[MontlyProfitItem]:
    """Get a list of monthly profits for a company for the year."""

    year_start = datetime(year, 1, 1)
    next_year_start = datetime(year + 1, 1, 1)
    month_number = cast(func.strftime("%m", InvoicesBriefTable.issue_date), Integer)

    sales = (
        select(
            month_number.label("month_number"),
            func.sum(InvoicesBriefTable.net_total).label("net_sales"),
        )
        .where(
            InvoicesBriefTable.seller_nip == company_nip,
            InvoicesBriefTable.issue_date >= year_start,
            InvoicesBriefTable.issue_date < next_year_start,
        )
        .group_by(month_number)
        .cte("sales")
    )

    costs = (
        select(
            month_number.label("month_number"),
            func.sum(InvoicesBriefTable.net_total).label("net_costs"),
        )
        .where(
            InvoicesBriefTable.buyer_nip == company_nip,
            InvoicesBriefTable.issue_date >= year_start,
            InvoicesBriefTable.issue_date < next_year_start,
        )
        .group_by(month_number)
        .cte("costs")
    )

    query = (
        select(
            sales.c.month_number,
            sales.c.net_sales,
            costs.c.net_costs,
            (sales.c.net_sales - costs.c.net_costs).label("net_profit"),
        )
        .select_from(sales.outerjoin(costs, sales.c.month_number == costs.c.month_number))
        .order_by(sales.c.month_number)
    )

    result = await db.execute(query)
    monthly_profits = [MontlyProfitItem(**month) for month in result.mappings().all()]

    return monthly_profits
