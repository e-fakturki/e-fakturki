from typing import Literal
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from backend.db.mappings.invoice_payment_mappings import PaymentStatus
from backend.schemas.ksef import SalesInvoicesRequest
from backend.db.models.invoices_brief import InvoicesBriefTable, KsefStatus
from backend.db.models.invoices_payment import InvoicesPaymentTable
from backend.schemas.invoices import InvoiceObjectRequest, InvoicesListResponse, PageInfo
from backend.db.mappings.invoice_details_mappings import parse_date


async def insert_invoice_brief_from_ksef(db: AsyncSession, invoice_data: dict) -> str:
    """Inserts a new invoice into the database."""
    try:
        invoice_record = InvoicesBriefTable(
            ksef_number=invoice_data.get("ksefNumber"),
            invoice_number=invoice_data["invoiceNumber"],
            issue_date=parse_date(invoice_data["issueDate"]),
            invoicing_date=parse_date(invoice_data["invoicingDate"]),
            acquisition_date=parse_date(invoice_data["acquisitionDate"]),
            permanent_storage_date=parse_date(invoice_data["permanentStorageDate"]),
            ksef_status="acc" if invoice_data["ksefNumber"] is not None else "not_sent",
            ###
            seller_name=invoice_data["seller"]["name"],
            seller_nip=invoice_data["seller"]["nip"],
            ###
            buyer_name=invoice_data["buyer"]["name"],
            buyer_nip=invoice_data["buyer"]["identifier"]["value"]
            if invoice_data["buyer"]["identifier"]["type"] == "Nip"
            else "",
            ###
            net_total=invoice_data["netAmount"],
            gross_total=invoice_data["grossAmount"],
            tax_total=invoice_data["vatAmount"],
            currency=invoice_data["currency"],
            ###
            invoicing_mode=invoice_data["invoicingMode"],
            invoice_type=invoice_data["invoiceType"],
            ###
            has_attachment=invoice_data["hasAttachment"],
            ###
            is_new=True,
        )

        db.add(invoice_record)
        await db.commit()
        await db.refresh(invoice_record)

        return invoice_record.id

    except IntegrityError:
        await db.rollback()
        return None


async def insert_invoice_brief_form_invoice_object(db: AsyncSession, invoice_data: InvoiceObjectRequest) -> str:
    """Extract data from InvoiceObjectRequest and insert it into the table."""
    try:
        invoice_record = InvoicesBriefTable(
            ksef_number=None,
            invoice_number=invoice_data.invoice_number,
            issue_date=parse_date(invoice_data.issue_date),
            invoicing_date=parse_date(invoice_data.invoicing_date),
            acquisition_date=parse_date(invoice_data.acquisition_date),
            permanent_storage_date=parse_date(invoice_data.permanent_storage_date),
            ksef_status=invoice_data.ksef_status,
            ###
            seller_name=invoice_data.seller_info.name,
            seller_nip=invoice_data.seller_info.nip,
            ###
            buyer_name=invoice_data.buyer_info.name,
            buyer_nip=invoice_data.buyer_info.nip,
            ###
            net_total=invoice_data.net_total,
            gross_total=invoice_data.gross_total,
            tax_total=invoice_data.tax_total,
            currency=invoice_data.currency,
            ###
            invoicing_mode=None,
            invoice_type=invoice_data.invoice_type,
            ###
            has_attachment=False,
            ###
            is_new=True,
        )

        db.add(invoice_record)
        await db.commit()
        await db.refresh(invoice_record)

        return invoice_record.id

    except IntegrityError:
        await db.rollback()
        raise


async def insert_invoice_brief_batch(
    db: AsyncSession, invoices: list[dict]
) -> list[str]:
    """Inserts a batch of invoices into the database."""
    return [await insert_invoice_brief_from_ksef(db, invoice) for invoice in invoices["invoices"]]


async def get_company_invoices_list(
    db: AsyncSession,
    filters: SalesInvoicesRequest,
    company_nip: str,
    invoice_type: Literal["sales", "purchase"],
) -> InvoicesListResponse:
    """Returns a list of invoices from the db, filtered and paginated."""

    # Decide on the filter condition
    if invoice_type == "sales":
        filter_condition = InvoicesBriefTable.seller_nip == company_nip
    elif invoice_type == "purchase":
        filter_condition = InvoicesBriefTable.buyer_nip == company_nip
    else:
        filter_condition = (InvoicesBriefTable.seller_nip == company_nip) | (
            InvoicesBriefTable.buyer_nip == company_nip
        )

    # Get total count of invoices
    total_items = await db.execute(
        select(func.count(InvoicesBriefTable.id)).where(
            and_(
                filter_condition,
                InvoicesBriefTable.issue_date >= parse_date(filters.date_from),
                InvoicesBriefTable.issue_date <= parse_date(filters.date_to),
            )
        )
    )
    total_items = total_items.scalar()

    # Query db with filters and pagination
    result = await db.execute(
        select(
            InvoicesBriefTable.id,
            InvoicesBriefTable.invoice_number,
            InvoicesBriefTable.issue_date,
            InvoicesBriefTable.is_new,
            InvoicesBriefTable.seller_name,
            InvoicesBriefTable.buyer_name,
            InvoicesBriefTable.gross_total,
            InvoicesBriefTable.currency,
            InvoicesBriefTable.ksef_number,
            InvoicesBriefTable.ksef_status,
        )
        .where(
            and_(
                filter_condition,
                InvoicesBriefTable.issue_date >= parse_date(filters.date_from),
                InvoicesBriefTable.issue_date <= parse_date(filters.date_to),
            )
        )
        .order_by(InvoicesBriefTable.issue_date.desc())
        .limit(filters.page_size)
        .offset(filters.page_offset)
    )
    data = [dict(row) for row in result.mappings().all()]

    page_info = PageInfo(
        current_page=(filters.page_offset // filters.page_size) + 1
        if total_items > 0
        else 1,
        page_size=filters.page_size,
        total_items=total_items,
        has_next_page=(filters.page_offset + filters.page_size) < total_items,
        has_previous_page=filters.page_offset > 0,
    )

    return InvoicesListResponse(invoices=data, page_info=page_info)


async def update_invoice_payment_status(
    db: AsyncSession, invoice_id: str, new_status: PaymentStatus
) -> bool:
    """Update the payment status of an invoice."""
    result = await db.execute(
        update(InvoicesPaymentTable)
        .where(InvoicesPaymentTable.invoice_id == invoice_id)
        .values(payment_status=new_status)
    )

    await db.commit()
    return result.rowcount > 0


async def update_invoice_is_new_status(
    db: AsyncSession, invoice_id: str, is_new: bool
) -> bool:
    """Update the is_new status of an invoice."""
    result = await db.execute(
        update(InvoicesBriefTable)
        .where(InvoicesBriefTable.id == invoice_id)
        .values(is_new=is_new)
    )

    await db.commit()
    return result.rowcount > 0


async def get_ksef_reference_number_by_invoice_id(
    db: AsyncSession, invoice_id: str
) -> str | None:
    """Get the KSeF reference number for the invoice with given ID."""
    result = await db.execute(
        select(InvoicesBriefTable.ksef_number).where(
            InvoicesBriefTable.id == invoice_id
        )
    )
    return result.scalar_one_or_none()


class InvoiceBriefResponse(BaseModel):
    """Response model for invoice brief."""

    id: str
    invoice_number: str
    invoice_type: str
    ksef_number: str | None
    invoicing_date: datetime | None
    acquisition_date: datetime | None
    permanent_storage_date: datetime | None
    ksef_status: KsefStatus
    is_new: bool
    issue_date: datetime
    ###
    seller_name: str
    seller_nip: str
    buyer_name: str
    buyer_nip: str
    ###
    currency: str
    net_total: float
    tax_total: float
    gross_total: float


async def get_invoice_brief_by_invoice_id(
    db: AsyncSession, invoice_id: str
) -> InvoiceBriefResponse:
    """Get the invoice details for the invoice with given ID."""
    stmt = select(
        InvoicesBriefTable.id,
        InvoicesBriefTable.invoice_number,
        InvoicesBriefTable.invoice_type,
        InvoicesBriefTable.ksef_number,
        InvoicesBriefTable.invoicing_date,
        InvoicesBriefTable.acquisition_date,
        InvoicesBriefTable.permanent_storage_date,
        InvoicesBriefTable.ksef_status,
        InvoicesBriefTable.is_new,
        InvoicesBriefTable.issue_date,
        InvoicesBriefTable.seller_name,
        InvoicesBriefTable.seller_nip,
        InvoicesBriefTable.buyer_name,
        InvoicesBriefTable.buyer_nip,
        InvoicesBriefTable.currency,
        InvoicesBriefTable.net_total,
        InvoicesBriefTable.tax_total,
        InvoicesBriefTable.gross_total,
    ).where(InvoicesBriefTable.id == invoice_id)

    execution_result = await db.execute(stmt)
    result = execution_result.mappings().one_or_none()
    return InvoiceBriefResponse(**result) if result else None
