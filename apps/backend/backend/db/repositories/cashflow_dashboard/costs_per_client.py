from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Integer, or_, case, cast, func, select

from backend.db.models.invoices_brief import InvoicesBriefTable
from backend.schemas.cashflow_dashboard import MonthlyProfitItem


async def get_monthly_profit_list(
    db: AsyncSession, company_nip: str, year: int
) -> list[MonthlyProfitItem]:
    """Get a list of monthly profits for a company for the year."""

    year_number = cast(func.strftime("%Y", InvoicesBriefTable.issue_date), Integer)
    month_number = cast(func.strftime("%m", InvoicesBriefTable.issue_date), Integer)

    is_sale = InvoicesBriefTable.seller_nip == company_nip
    is_cost = InvoicesBriefTable.buyer_nip == company_nip

    sales_total = func.sum(case((is_sale, InvoicesBriefTable.net_total), else_=0))
    costs_total = func.sum(case((is_cost, InvoicesBriefTable.net_total), else_=0))

    query = (
        select(
            month_number.label("month_number"),
            sales_total.label("net_sales"),
            costs_total.label("net_costs"),
            (sales_total - costs_total).label("net_profit"),
        )
        .where(
            or_(is_sale, is_cost),
            year_number == year,
        )
        .group_by(month_number)
        .order_by(month_number)
    )

    result = await db.execute(query)

    return [MonthlyProfitItem(**month) for month in result.mappings().all()]
