from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Integer, or_, case, cast, func, select

from backend.db.models.invoices_brief import InvoicesBriefTable
from backend.schemas.cashflow_dashboard import ContractorCashflowItem, CASHFLOW_TYPE


async def get_cashflow_per_contractor(
    db: AsyncSession,
    company_nip: str,
    year: int,
    month: int,
    cashflow_type: CASHFLOW_TYPE,
) -> list[ContractorCashflowItem]:
    """Get a sum of sales/purchases per contractor for a company for the month/year."""

    year_number = cast(func.strftime("%Y", InvoicesBriefTable.issue_date), Integer)
    month_number = cast(func.strftime("%m", InvoicesBriefTable.issue_date), Integer)

    is_sale = InvoicesBriefTable.seller_nip == company_nip
    is_cost = InvoicesBriefTable.buyer_nip == company_nip
    contractor_nip = (
        InvoicesBriefTable.buyer_nip
        if cashflow_type == "sales"
        else InvoicesBriefTable.seller_nip
    )
    contractor_name = (
        InvoicesBriefTable.buyer_name
        if cashflow_type == "sales"
        else InvoicesBriefTable.seller_name
    )

    sales_total = func.sum(case((is_sale, InvoicesBriefTable.net_total), else_=0))
    costs_total = func.sum(case((is_cost, InvoicesBriefTable.net_total), else_=0))
    cashflow_total = sales_total if cashflow_type == "sales" else costs_total

    query = (
        select(
            contractor_nip.label("contractor_nip"),
            contractor_name.label("contractor_name"),
            cashflow_total.label("net_cashflow"),
        )
        .where(
            (is_sale if cashflow_type == "sales" else is_cost),
            year_number == year,
            month_number == month,
        )
        .group_by(contractor_nip)
        .order_by(cashflow_total.desc())
    )

    result = await db.execute(query)

    return [
        ContractorCashflowItem(
            year_number=year,
            month_number=month,
            contractor_nip=item["contractor_nip"],
            contractor_name=item["contractor_name"],
            net_cashflow=item["net_cashflow"],
        )
        for item in result.mappings().all()
    ]
