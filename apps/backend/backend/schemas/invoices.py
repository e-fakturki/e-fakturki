from pydantic import BaseModel
from datetime import datetime

from backend.db.models.invoices_payment import PaymentStatus, PaymentType
from backend.db.models.invoices_brief import KsefStatus
from backend.schemas.common import PageInfo


class InvoicesListResponse(BaseModel):
    """Response model for invoice list with pagination info."""

    invoices: list[dict]
    page_info: PageInfo


class InvoiceCompanyData(BaseModel):
    """Response model for invoice buyer and seller detals."""

    name: str
    nip: str
    address_l1: str | None
    address_l2: str | None
    email: str | None
    phone: str | None


class InvoiceEntry(BaseModel):
    """Response model for invoice list entry."""

    row_number: int
    delivery_date: str | datetime | None
    name: str
    amount: float
    unit: str
    net_price: float | None
    gross_price: float | None
    net_total: float | None
    tax_rate: int
    tax_total: float | None
    gross_total: float | None


class InvoicePayment(BaseModel):
    """Response model for invoice payment."""

    payment_status: PaymentStatus
    payment_type: PaymentType
    payment_date: str | datetime | None
    payment_due_date: str | datetime | None
    partial_payments: str | None
    seller_bank_account_number: str | None
    seller_bank_name: str | None


class InvoiceResponse(BaseModel):
    """Response model for full invoice with details."""

    id: str
    invoice_number: str
    invoice_type: str
    ksef_number: str | None
    invoicing_date: datetime | None
    acquisition_date: datetime | None
    permanent_storage_date: datetime | None
    ksef_status: KsefStatus
    is_new: bool
    ###
    issue_date: datetime
    issue_place: str | None
    ###
    seller_info: InvoiceCompanyData
    buyer_info: InvoiceCompanyData
    ###
    entries: list[InvoiceEntry]
    ###
    currency: str
    net_total: float
    tax_total: float
    gross_total: float
    ###
    payment: InvoicePayment | None
    ###
    annotations: str | None
    additional_info: str | None
    footer_info: str | None
    footer_registers: str | None


# temp models later merg with the upper ones 

class InvoiceEntryRequest(BaseModel):
    """Request model for invoice entry."""
    row_number: int
    delivery_date: str | None
    name: str
    amount: float
    unit: str
    net_price: float
    gross_price: float | None
    net_total: float
    tax_rate: str
    tax_total: float | None
    gross_total: float

class InvoiceCompanyDataRequest(BaseModel):
    """Request model for invoice buyer and seller detals."""
    name: str
    nip: str
    krs: str | None
    regon: str | None
    country_code: str
    address_l1: str | None
    address_l2: str | None
    address_correspondance_l1: str | None
    address_correspondance_l2: str | None
    email: str | None
    phone_number: str | None


class InvoicePaymentRequest(BaseModel):
    """Request model for invoice payment."""
    payment_status: str
    payment_type: int
    payment_date: str | None
    payment_due_date: str | None
    partial_payments: str | None
    seller_bank_account_number: str | None
    seller_bank_name: str | None


class InvoiceObjectRequest(BaseModel):
    """Request model for full invoice with details.+"""
    id: str | None
    invoice_number: str
    invoice_type: str
    ksef_number: str | None
    invoicing_date: str | None
    acquisition_date: str | None
    permanent_storage_date: str | None
    ksef_status: str
    is_new: bool
    issue_date: str
    issue_place: str
    seller_info: InvoiceCompanyDataRequest
    buyer_info: InvoiceCompanyDataRequest
    entries: list[InvoiceEntryRequest]
    currency: str
    net_total: float
    tax_total: float
    gross_total: float
    payment: InvoicePaymentRequest
    annotations: str | None
    additional_info: str | None
    footer_info: str | None
    footer_registers: str | None
