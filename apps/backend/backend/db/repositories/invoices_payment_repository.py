from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from backend.db.mappings.invoice_details_mappings import parse_date
from backend.schemas.invoices import InvoiceObjectRequest, InvoicePayment
from backend.db.models.invoices_payment import InvoicesPaymentTable, PaymentStatus, PaymentType
from backend.db.mappings.invoice_payment_mappings import (
    map_fa3_fa_platnosc_to_invoices_payment_table,
)
import backend.domain.fa3_xml_utils.models.schemat as fa3utils


async def insert_invoice_payment_details(
    db: AsyncSession, fa3: fa3utils.Faktura, invoice_id: str
) -> str | None:
    """Insert parsed invoice payment details into InvoicesPaymentTable."""
    try:
        if fa3.fa.platnosc is None:
            return None

        invoice_payment_record = map_fa3_fa_platnosc_to_invoices_payment_table(
            fa3.fa.platnosc, invoice_id
        )

        db.add(invoice_payment_record)
        await db.commit()
        await db.refresh(invoice_payment_record)

        return invoice_payment_record.id

    except IntegrityError:
        await db.rollback()
        return None


async def insert_invoice_payment_details_from_invoice_object(
    db: AsyncSession, invoice_data: InvoiceObjectRequest, invoice_id: str
) -> str | None:
    """Extract data from InvoiceObjectRequest and insert it into the table."""
    try:
        payment_type = PaymentType.cash
        if invoice_data.payment.payment_type != 1:
            payment_type = PaymentType(invoice_data.payment.payment_type)

        payment_status = PaymentStatus.unpaid
        if invoice_data.payment.payment_status != "unpaid":
            payment_status = PaymentStatus.paid

        invoice_payment_record = InvoicesPaymentTable(
            invoice_id=invoice_id,
            payment_type=payment_type,
            payment_status=payment_status,
            payment_due_date=parse_date(invoice_data.payment.payment_due_date),
            payment_date=parse_date(invoice_data.payment.payment_date),
            seller_bank_account_number=invoice_data.payment.seller_bank_account_number,
            seller_bank_name=invoice_data.payment.seller_bank_name,
        )

        db.add(invoice_payment_record)
        await db.commit()
        await db.refresh(invoice_payment_record)

        return invoice_payment_record.id

    except IntegrityError:
        await db.rollback()
        raise


async def get_invoice_payment_by_invoice_id(
    db: AsyncSession, invoice_id: str
) -> InvoicePayment:
    """Get the invoice payment info for the invoice with given ID."""
    stmt = select(
        InvoicesPaymentTable.payment_status,
        InvoicesPaymentTable.payment_type,
        InvoicesPaymentTable.payment_date,
        InvoicesPaymentTable.payment_due_date,
        InvoicesPaymentTable.partial_payments,
        InvoicesPaymentTable.seller_bank_account_number,
        InvoicesPaymentTable.seller_bank_name,
    ).where(InvoicesPaymentTable.invoice_id == invoice_id)

    execution_result = await db.execute(stmt)
    result = execution_result.mappings().one_or_none()
    return InvoicePayment(**result) if result else None
