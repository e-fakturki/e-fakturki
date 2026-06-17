from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.invoices import PageInfo


class CompanyBase(BaseModel):
    """Base schema for a company."""

    model_config = ConfigDict(from_attributes=True)

    owner_id: str | None = Field(
        None, description="The ID of the user who owns the company."
    )
    name: str = Field(..., description="The name of the company.")
    nip: str = Field(
        ..., description="The NIP (tax identification number) of the company."
    )
    krs: str | None = Field(
        None,
        description="The KRS (National Court Register) number of the company, if applicable.",
    )
    regon: str | None = Field(
        None,
        description="The REGON (statistical number) of the company, if applicable.",
    )
    country_code: str = Field(..., description="Country the company is registered in.")
    address_l1: str | None = Field(None, description="First line of company's address.")
    address_l2: str | None = Field(
        None, description="Second line of company's address."
    )
    address_correspondance_l1: str | None = Field(
        None, description="First line of company's correspondance address."
    )
    address_correspondance_l2: str | None = Field(
        None, description="Second line of company's correspondance address."
    )
    email: str | None = Field(None, description="Company's email address.")
    phone_number: str | None = Field(None, description="Company's phone number.")
    additional_info: str | None = Field(
        None, description="Any additional info about the company."
    )


class CompanyCreate(CompanyBase):
    """Schema for creating company."""


class CompanyCreateResponse(BaseModel):
    """Return schema for creating a new company record."""

    owner_id: str | None = Field(
        None, description="The ID of the user who owns the company."
    )
    id: str = Field(
        ..., description="The ID of the created company record in the database."
    )


class CompanyReadUpdate(CompanyBase):
    """Schema for reading/updating company."""

    id: str = Field(..., description="Company ID.")


class UserCompanyResponse(CompanyBase):
    """Return schema for fetching a user's company information."""

    id: str = Field(..., description="The ID of the company record in the database.")
    ksef_authorized: bool = Field(
        ..., description="Indicates whether the company is authorized to use KSeF."
    )


class CompaniesListResponse(BaseModel):
    """Return schema for companies list."""

    companies: list[CompanyReadUpdate]
    page_info: PageInfo


class IsoCountry(BaseModel):
    """Return schema for ISO countries list."""

    label: str
    value: str
