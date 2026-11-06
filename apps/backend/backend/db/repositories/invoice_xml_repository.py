from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.invoice_xml_snapshots import InvoiceXmlSnapshotsTable


async def insert_invoice_xml(
    db_session: AsyncSession, invoice_id: str, xml: str, sha256_base64: str | None
) -> None:
    """Inserts invoice XML into the database."""
    stmt = InvoiceXmlSnapshotsTable(
        invoice_id=invoice_id, xml=xml, sha256_base64=sha256_base64
    )
    db_session.add(stmt)
    await db_session.commit()


async def get_invoice_xml(db_session: AsyncSession, invoice_id: str) -> str:
    """Loads invoice xml from the database."""
    stmt = (
        select(InvoiceXmlSnapshotsTable.xml)
        .where(InvoiceXmlSnapshotsTable.invoice_id == invoice_id)
        .limit(1)
    )

    result = await db_session.execute(stmt)
    xml = result.scalar_one_or_none()

    if xml is None:
        raise ValueError(f"Invoice XML not found (invoice_id={invoice_id})")

    return xml


async def check_if_invoice_xml_exists(
    db_session: AsyncSession, invoice_id: str
) -> bool:
    """Checks if invoice XML exists in the database."""
    stmt = (
        select(InvoiceXmlSnapshotsTable.invoice_id)
        .where(InvoiceXmlSnapshotsTable.invoice_id == invoice_id)
        .limit(1)
    )

    result = await db_session.execute(stmt)
    return result.scalar_one_or_none() is not None
