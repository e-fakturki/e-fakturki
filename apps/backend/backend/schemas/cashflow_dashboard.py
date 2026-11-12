from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field

from backend.db.models.invoices_payment import PaymentStatus

CASHFLOW_TYPE = Literal["sales", "purchases"]
SALE_TYPE = Literal["invoice", "bill", "other"]
COST_TYPE = Literal["invoice", "operational", "salary", "tax", "insurance", "lease", "other"]
SORT_CASHFLOW_LIST_BY = Literal["year_number", "month_number", "net_value"]
SORT_ORDER = Literal["asc", "desc"]


class MontlyProfitItem(BaseModel):
    """Schema for monthly profit list item."""

    month_number: int | None = Field(
        None, description="Month number eg. 1 - January, 11 - November"
    )

    net_sales: float | None = Field(None, description="Net sales per month")
    net_costs: float | None = Field(None, description="Net costs per month")

    net_profit: float | None = Field(
        None, description="Net profit per month (net_sales - net_costs)"
    )


class MonthlyProfitSummary(BaseModel):
    """Schema for monthly profit summary."""
    year_number: int | None = Field(
        None, description="Year number eg. 2026"
    )
    month_number: int | None = Field(
        None, description="Month number eg. 1 - January, 11 - November"
    )
    
    sales_amount: int | None = Field(None, description="Number of sales for the month")
    avg_sale_value: float | None = Field(None, description="Average sale value for the month")
    costs_amount: int | None = Field(None, description="Number of costs for the month")
    avg_cost_value: float | None = Field(None, description="Average cost value for the month")

    new_customers: int | None = Field(None, description="Number of new customers for the month")
    inactive_customers: int | None = Field(None, description="Number of inactive customers for the month")

    unpaid_sales: int | None = Field(None, description="Number of unpaid sales for the month")
    unpaid_costs: int | None = Field(None, description="Number of unpaid costs for the month")


class CashflowListItem(BaseModel):
    """Schema for item of cashflow dashboard sales/costs list. """

    year_number: int | None = Field(
        None, description="Year number eg. 2026"
    )
    month_number: int | None = Field(
        None, description="Month number eg. 1 - January, 11 - November"
    )

    id: str | None = Field(None, description="ID of the cashflow item / invoice")
    issue_date: datetime | None = Field(None, description="Issue date of the cashflow item")
    type: SALE_TYPE | COST_TYPE | None = Field(None, description="Type of the cashflow item")
    contractor_name: str | None = Field(None, description="Name of the contractor")
    net_value: float | None = Field(None, description="Net value of the cashflow item")
    payment_status: PaymentStatus | None = Field(None, description="Payment status of the cashflow item")