from pydantic import BaseModel, Field

from backend.domain.fa3_xml_utils.models.schemat import TstawkaPodatku
from backend.schemas.common import PageInfo


class ProductCreate(BaseModel):
    """Schema for creating a new product record."""

    company_id: str = Field(..., description="ID of the company that owns the product")

    name: str = Field(..., description="Product name")
    description: str | None = Field(None, description="Product description")
    gtin: str | None = Field(
        None, description="Product GTIN (Global Trade Item Number)"
    )

    unit: str | None = Field(None, description="Unit of measurement (e.g. pcs, kg)")

    net_price: float | None = Field(None, description="Net price (without tax)")
    tax_rate: str | None = Field(None, description="Tax rate in percent (e.g. 23)")
    gross_price: float | None = Field(
        None,
        description="Gross price (with tax). If not provided, it will be calculated automatically",
    )


class ProductCreateResponse(BaseModel):
    """Response schema for creating a product record."""

    id: str = Field(..., description="ID of the product record")
    company_id: str = Field(..., description="ID of the company that owns the product")


class ProductUpdate(ProductCreate):
    """Schema for updating a product."""

    id: str = Field(..., description="Product ID.")


class ProductListItem(BaseModel):
    """Schema for product list item."""

    id: str = Field(..., description="The ID of the product record in the database.")

    name: str = Field(..., description="Product name")
    description: str | None = Field(None, description="Product description")
    gtin: str | None = Field(
        None, description="Product GTIN (Global Trade Item Number)"
    )

    unit: str | None = Field(None, description="Unit of measurement (e.g. pcs, kg)")

    net_price: float | None = Field(..., description="Net price (without tax)")
    tax_rate: TstawkaPodatku | None = Field(
        ..., description="Tax rate in percent (e.g. 23)"
    )
    gross_price: float | None = Field(
        None,
        description="Gross price (with tax). If not provided, it will be calculated automatically",
    )


class ProductListResponse(BaseModel):
    """Return schema for products list."""

    products: list[ProductListItem]
    page_info: PageInfo


class TaxRate(BaseModel):
    """Schema for tax rate."""

    display_text: str
    hint_text: str
    str_repr: str
    value: float
