from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Integer, and_, case, cast, func, literal, select, outerjoin

from backend.db.models.invoices_payment import InvoicesPaymentTable
from backend.db.models.invoices_brief import InvoicesBriefTable
from backend.schemas.cashflow_dashboard import (MontlyProfitItem, MonthlyProfitSummary)


async def get_monthly_profit_list(
    db: AsyncSession, company_nip: str, year: int
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
        .select_from(
            sales.outerjoin(costs, sales.c.month_number == costs.c.month_number)
        )
        .order_by(sales.c.month_number)
    )

    result = await db.execute(query)

    return [MontlyProfitItem(**month) for month in result.mappings().all()]


async def get_month_summary(
    db: AsyncSession, 
    company_nip: str, 
    year: int, 
    month: int,
) -> MonthlyProfitSummary:
    """Get a summary of a specific month for a company."""

    current_month_start = datetime(year, month, 1)
    next_month_start = (
        datetime(year + 1, 1, 1)
        if month == 12
        else datetime(year, month + 1, 1)
    )
    previous_month_start = (
        datetime(year - 1, 12, 1)
        if month == 1
        else datetime(year, month - 1, 1)
    )

    month_number = literal(month).label("month_number")
    year_number = literal(year).label("year_number")
    payment_is_unpaid = InvoicesPaymentTable.payment_status == "unpaid"

    previous_month_customers = (
        select(InvoicesBriefTable.buyer_nip.label("buyer_nip"))
        .distinct()
        .where(
            InvoicesBriefTable.seller_nip == company_nip,
            InvoicesBriefTable.issue_date >= previous_month_start,
            InvoicesBriefTable.issue_date < current_month_start,
            InvoicesBriefTable.buyer_nip.is_not(None),
        )
        .cte("previous_month_customers")
    )

    current_month_customer_exists = (
        select(1)
        .select_from(InvoicesBriefTable)
        .where(
            InvoicesBriefTable.seller_nip == company_nip,
            InvoicesBriefTable.buyer_nip == previous_month_customers.c.buyer_nip,
            InvoicesBriefTable.issue_date >= current_month_start,
            InvoicesBriefTable.issue_date < next_month_start,
        )
        .exists()
    )

    inactive_customers = (
        select(previous_month_customers.c.buyer_nip)
        .where(~current_month_customer_exists)
        .cte("inactive_customers")
    )

    previous_month_customer_exists = (
        select(1)
        .select_from(previous_month_customers)
        .where(
            previous_month_customers.c.buyer_nip == InvoicesBriefTable.buyer_nip
        )
        .exists()
    )

    new_customers = (
        select(InvoicesBriefTable.buyer_nip.label("buyer_nip"))
        .distinct()
        .where(
            InvoicesBriefTable.seller_nip == company_nip,
            InvoicesBriefTable.issue_date >= current_month_start,
            InvoicesBriefTable.issue_date < next_month_start,
            InvoicesBriefTable.buyer_nip.is_not(None),
            ~previous_month_customer_exists,
        )
        .cte("new_customers")
    )

    sales = (
        select(
            year_number,
            month_number,
            func.count().label("sales_amount"),
            func.round(func.avg(InvoicesBriefTable.net_total), 2).label(
                "avg_sale_value"
            ),
            func.count(case((payment_is_unpaid, 1))).label("unpaid_sales"),
            select(func.count()).select_from(new_customers).scalar_subquery().label(
                "new_customers"
            ),
            select(func.count())
            .select_from(inactive_customers)
            .scalar_subquery()
            .label("inactive_customers"),
        )
        .select_from(
            outerjoin(
                InvoicesBriefTable,
                InvoicesPaymentTable,
                InvoicesBriefTable.id == InvoicesPaymentTable.invoice_id,
            )
        )
        .where(
            InvoicesBriefTable.seller_nip == company_nip,
            InvoicesBriefTable.issue_date >= current_month_start,
            InvoicesBriefTable.issue_date < next_month_start,
        )
        .cte("sales")
    )

    costs = (
        select(
            year_number,
            month_number,
            func.count().label("costs_amount"),
            func.round(func.avg(InvoicesBriefTable.net_total), 2).label(
                "avg_cost_value"
            ),
            func.count(case((payment_is_unpaid, 1))).label("unpaid_costs"),
        )
        .select_from(
            outerjoin(
                InvoicesBriefTable,
                InvoicesPaymentTable,
                InvoicesBriefTable.id == InvoicesPaymentTable.invoice_id,
            )
        )
        .where(
            InvoicesBriefTable.buyer_nip == company_nip,
            InvoicesBriefTable.issue_date >= current_month_start,
            InvoicesBriefTable.issue_date < next_month_start,
        )
        .cte("costs")
    )

    query = (
        select(
            sales.c.year_number,
            sales.c.month_number,
            sales.c.sales_amount,
            sales.c.avg_sale_value,
            sales.c.new_customers,
            sales.c.unpaid_sales,
            costs.c.costs_amount,
            costs.c.avg_cost_value,
            sales.c.inactive_customers,
            costs.c.unpaid_costs,
        )
        .select_from(
            sales.join(
                costs,
                and_(
                    sales.c.month_number == costs.c.month_number,
                    sales.c.year_number == costs.c.year_number,
                ),
            )
        )
    )

    result = await db.execute(query)
    summary = result.mappings().one()

    return MonthlyProfitSummary(**summary)

    