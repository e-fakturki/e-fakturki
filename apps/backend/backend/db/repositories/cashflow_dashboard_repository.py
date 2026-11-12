from datetime import datetime
from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Integer, and_, or_, case, cast, func, literal, select, outerjoin

from backend.db.models.invoices_payment import InvoicesPaymentTable
from backend.db.models.invoices_brief import InvoicesBriefTable
from backend.schemas.cashflow_dashboard import CASHFLOW_TYPE, SORT_CASHFLOW_LIST_BY, SORT_ORDER, CashflowListItem, MontlyProfitItem, MonthlyProfitSummary


async def get_monthly_profit_list(
    db: AsyncSession, company_nip: str, year: int
) -> list[MontlyProfitItem]:
    """Get a list of monthly profits for a company for the year."""

    year_number = cast(func.strftime("%Y", InvoicesBriefTable.issue_date), Integer)
    month_number = cast(func.strftime("%m", InvoicesBriefTable.issue_date), Integer)


    is_sale = InvoicesBriefTable.seller_nip == company_nip
    is_cost = InvoicesBriefTable.buyer_nip == company_nip

    sales_total = func.sum(
        case((is_sale, InvoicesBriefTable.net_total), else_ = 0)
    )
    costs_total = func.sum(
        case((is_cost, InvoicesBriefTable.net_total), else_ = 0)
    )

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


async def get_cashflow_list_lazy(
    db: AsyncSession, 
    company_nip: str, 
    year: int, 
    month: int,
    type: CASHFLOW_TYPE,
    offset: int,
    limit: int,
    sort_by: SORT_CASHFLOW_LIST_BY | None = None,
    sort_order: SORT_ORDER | None = None,
) -> list[CashflowListItem]:
    """Get a lazy list of cashflow items for the specified company, year, and month."""

    month_number = cast(func.strftime("%m", InvoicesBriefTable.issue_date), Integer)
    year_number = cast(func.strftime("%Y", InvoicesBriefTable.issue_date), Integer)

    is_sale = InvoicesBriefTable.seller_nip == company_nip
    is_cost = InvoicesBriefTable.buyer_nip == company_nip
    contractor_name = (
        InvoicesBriefTable.buyer_name
        if type == "sales"
        else InvoicesBriefTable.seller_name
    )
    sort_columns = {
        "date": InvoicesBriefTable.issue_date,
        "type": InvoicesBriefTable.invoice_type,
        "contractor_name": contractor_name,
        "net_value": InvoicesBriefTable.net_total,
        "payment_status": InvoicesPaymentTable.payment_status,
    }
    sort_column = sort_columns.get(sort_by, InvoicesBriefTable.issue_date)
    sort_expression = sort_column.asc() if sort_order == "asc" else sort_column.desc()


    result = await db.execute(
        select(
            InvoicesBriefTable.id,
            InvoicesBriefTable.issue_date,
            contractor_name.label("contractor_name"),
            InvoicesBriefTable.net_total.label("net_value"),
            InvoicesPaymentTable.payment_status,
        )
        .select_from(
            outerjoin(
                InvoicesBriefTable,
                InvoicesPaymentTable,
                InvoicesBriefTable.id == InvoicesPaymentTable.invoice_id,
            )
        )
        .where(
            and_(
                (is_sale if type == "sales" else is_cost),
                year_number == year,
                month_number == month,
            )
        )
        .order_by(sort_expression, InvoicesBriefTable.id.asc())
        .limit(limit)
        .offset(offset)
    )

    return [CashflowListItem(
        year_number=year,
        month_number=month,
        id=item["id"],
        issue_date=item["issue_date"],
        type="invoice",
        contractor_name=item["contractor_name"],
        net_value=item["net_value"],
        payment_status=item["payment_status"]
    ) for item in result.mappings().all()]