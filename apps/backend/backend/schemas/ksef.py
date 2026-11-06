"""Schemas for KSeF Communication."""

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field


class CredentialsCreate(BaseModel):
    """Schema for creating KSeF credentials."""

    company_id: str = (
        Form(
            ..., description="The ID of the company to which the certificates belong."
        ),
    )
    certificates_for_auth: bool = (
        Form(
            ...,
            description="Whether the uploaded certificates are for authentication (True) or for offline mode (False).",
        ),
    )
    certificate: UploadFile = (
        File(..., description="The certificate file to be uploaded."),
    )
    private_key: UploadFile = (
        File(..., description="The private key file to be uploaded."),
    )
    password: str = Form(..., description="The password for the private key.")


class CredentialsCreateResponse(BaseModel):
    """Return schema for creating KSeF credentials."""

    company_id: str = Field(
        ..., description="The ID of the company to which the certificates belong."
    )
    credentials_id: str = Field(
        ...,
        description="The ID of the created KSeF credentials record in the database.",
    )


class KsefInvoiceUploadStatus(BaseModel):
    """Schema for reading invoice KSeF upload status."""

    company_id: str = Field(
        ..., description="The ID of the company that issued the invoice."
    )
    invoice_id: int = Field(
        ..., description="The ID of the invoice that was uploaded to KSeF."
    )

    ksef_status: int = Field(
        ...,
        description="The status of the invoice in KSeF, e.g. 'pending', 'accepted', 'rejected'.",
    )
    ksef_reference_number: str | None = Field(
        None,
        description="The reference number returned by KSeF after uploading the invoice, if available.",
    )


class KsefCertificatesLoad(BaseModel):
    """Schema for storing KSeF certificates for a company. Encrypted or decrypted."""

    certificate: str | bytes
    private_key: str | bytes
    password: str | bytes


class KsefInvoiceDownload(BaseModel):
    """Schema for downloading invoice from KSeF."""

    company_id: str
    invoice_id: str

    data: str


class SalesInvoicesRequest(BaseModel):
    """Schema for requesting sales invoices metadata list from KSeF."""

    company_id: str = Field(
        ..., description="The ID of the company selected in the system as the seller."
    )
    date_from: str = Field(
        ...,
        description="The start date of the date range for which to retrieve invoice metadata (yyyy-mm-dd)",
    )
    date_to: str = Field(
        ...,
        description="The end date of the date range for which to retrieve invoice metadata (yyyy-mm-dd)",
    )
    page_size: int = Field(
        10,
        description="The number of invoice metadata records to retrieve per page. [10 ... 250]",
    )
    page_offset: int = Field(
        0,
        description="The offset for pagination, i.e. the number of records to skip before starting to collect the result set.",
    )
