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
