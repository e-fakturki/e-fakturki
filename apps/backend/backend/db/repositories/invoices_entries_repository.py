from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.db.mappings.invoice_details_mappings import parse_date
from backend.schemas.invoices import InvoiceEntry, InvoiceObjectRequest
from backend.db.models.invoice_entries import InvoiceEntriesTable
from backend.db.mappings.invoices_entries_mappings import (
    map_fa3_fawiersz_to_invoice_entries_table,
    parse_tax_rate,
)
import backend.domain.fa3_xml_utils.models.schemat as fa3utils


async def insert_invoice_entries(
    db: AsyncSession, fa3: fa3utils.Faktura, invoice_id: str
) -> list[str] | None:
    """Insert parsed invoice entries into InvoiceEntriesTable."""
    invoice_entries = []
    for entry in fa3.fa.fa_wiersz:
        invoice_entry = map_fa3_fawiersz_to_invoice_entries_table(entry, invoice_id)
        db.add(invoice_entry)
        await db.commit()
        await db.refresh(invoice_entry)
        invoice_entries.append(invoice_entry)

    return [entry.id for entry in invoice_entries]


async def insert_invoice_entries_from_invoice_object(
    db: AsyncSession, invoice_data: InvoiceObjectRequest, invoice_id: str
) -> str | None:
    """Extract data from InvoiceObjectRequest and insert it into the table."""
    try:
        invoice_entries = []

        for entry in invoice_data.entries:
            invoice_entries_record = InvoiceEntriesTable(
                invoice_id=invoice_id,
                row_number=entry.row_number,
                uu_id=None,
                gtin=None,
                delivery_date=parse_date(entry.delivery_date),
                name=entry.name,
                index=None,
                amount=entry.amount,
                unit=entry.unit,
                net_price=entry.net_price,
                gross_price=entry.gross_price,
                discount=None,
                net_total=entry.net_total,
                tax_rate=parse_tax_rate(entry.tax_rate),
                tax_total=entry.tax_total,
                gross_total=entry.gross_total,
            )

            db.add(invoice_entries_record)
            await db.commit()
            await db.refresh(invoice_entries_record)
            invoice_entries.append(invoice_entries_record)

        return [entry.id for entry in invoice_entries]

    except IntegrityError:
        await db.rollback()
        raise


async def get_invoice_entries_by_invoice_id(
    db: AsyncSession, invoice_id: str
) -> InvoiceEntry:
    """Get the invoice entries for the invoice with given ID."""
    stmt = select(
        InvoiceEntriesTable.row_number,
        InvoiceEntriesTable.delivery_date,
        InvoiceEntriesTable.name,
        InvoiceEntriesTable.amount,
        InvoiceEntriesTable.unit,
        InvoiceEntriesTable.net_price,
        InvoiceEntriesTable.gross_price,
        InvoiceEntriesTable.net_total,
        InvoiceEntriesTable.tax_rate,
        InvoiceEntriesTable.tax_total,
        InvoiceEntriesTable.gross_total,
    ).where(InvoiceEntriesTable.invoice_id == invoice_id)

    execution_result = await db.execute(stmt)
    result = execution_result.mappings().all()
    return [InvoiceEntry(**entry) for entry in result]
