from pydantic import BaseModel, Field


class MontlyProfitItem(BaseModel):
    """Schema for product list item."""

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