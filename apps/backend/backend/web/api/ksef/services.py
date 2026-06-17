from sqlalchemy.ext.asyncio import AsyncSession
from dateutil import parser

from backend.schemas.ksef import KsefCertificatesLoad
from backend.services.encryptor import Encryptor
from backend.db.repositories.invoice_xml_repository import insert_invoice_xml
from backend.db.repositories.invoices_details_repository import (
    insert_invoice_details,
    get_invoice_details_by_invoice_id,
)
from backend.db.repositories.invoices_entries_repository import (
    insert_invoice_entries,
    get_invoice_entries_by_invoice_id,
)
from backend.db.repositories.invoices_brief_repository import (
    get_invoice_brief_by_invoice_id,
)
from backend.db.repositories.invoices_payment_repository import (
    insert_invoice_payment_details,
    get_invoice_payment_by_invoice_id,
    InvoicePayment,
)
from backend.domain.fa3_xml_utils.utils.parser import FA3XmlParser
from backend.schemas.invoices import InvoiceResponse, InvoiceCompanyData


def to_iso(date_str: str, end_of_day: bool = False) -> str:
    """Converts date string to ISO format."""
    dt = parser.parse(date_str)

    if end_of_day:
        dt = dt.replace(hour=23, minute=59, second=59)
    else:
        dt = dt.replace(hour=0, minute=0, second=0)

    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def decrypt_ksef_certs(certificates: KsefCertificatesLoad) -> KsefCertificatesLoad:
    """Decrypts KSeF certificates."""
    certificates.certificate = Encryptor().decrypt_text(certificates.certificate)
    certificates.private_key = Encryptor().decrypt_text(certificates.private_key)
    certificates.password = Encryptor().decrypt_text(certificates.password)

    return certificates


async def parse_and_insert_full_invoice(
    db_session: AsyncSession, invoice_id: str, invoice_xml: dict[str, str]
) -> None:
    """
    Parses invoice XML (creates invoice object) and inserts corresponding data into:
    InvoiceXmlSnapshotsTable,
    InvoiceDetailsTable,
    InvoiceEntriesTable and
    InvoicesPaymentsTable.
    """
    parser = FA3XmlParser()
    fa3_inv = parser.parse_string(invoice_xml.content)

    await insert_invoice_xml(
        db_session,
        invoice_id,
        invoice_xml.content,
        invoice_xml.sha256_base64,
    )
    await insert_invoice_details(db_session, fa3_inv, invoice_id)
    await insert_invoice_entries(db_session, fa3_inv, invoice_id)
    await insert_invoice_payment_details(db_session, fa3_inv, invoice_id)

    await db_session.commit()


async def build_invoice_details_response(
    db: AsyncSession, invoice_id: str
) -> InvoiceResponse:
    """
    Collect all the data needed from the db to build the invoice response.
    Create, format and return the InvoiceResponse object.
    """
    inv_brief_data = await get_invoice_brief_by_invoice_id(db, invoice_id)
    inv_detailed_data = await get_invoice_details_by_invoice_id(db, invoice_id)
    inv_entries_data = await get_invoice_entries_by_invoice_id(db, invoice_id)
    inv_payment_data = await get_invoice_payment_by_invoice_id(db, invoice_id)

    return InvoiceResponse(
        id=inv_brief_data.id,
        invoice_number=inv_brief_data.invoice_number,
        invoice_type=inv_brief_data.invoice_type,
        ksef_number=inv_brief_data.ksef_number,
        invoicing_date=inv_brief_data.invoicing_date,
        acquisition_date=inv_brief_data.acquisition_date,
        permanent_storage_date=inv_brief_data.permanent_storage_date,
        ksef_status=inv_brief_data.ksef_status,
        is_new=inv_brief_data.is_new,
        issue_date=inv_brief_data.issue_date,
        issue_place=inv_detailed_data.issue_place,
        seller_info=InvoiceCompanyData(
            name=inv_brief_data.seller_name,
            nip=inv_brief_data.seller_nip,
            address_l1=inv_detailed_data.seller_address_l1,
            address_l2=inv_detailed_data.seller_address_l2,
            email=inv_detailed_data.seller_email,
            phone=inv_detailed_data.seller_phone,
        ),
        buyer_info=InvoiceCompanyData(
            name=inv_brief_data.buyer_name,
            nip=inv_brief_data.buyer_nip,
            address_l1=inv_detailed_data.buyer_address_l1,
            address_l2=inv_detailed_data.buyer_address_l2,
            email=inv_detailed_data.buyer_email,
            phone=inv_detailed_data.buyer_phone,
        ),
        entries=inv_entries_data,
        currency=inv_brief_data.currency,
        net_total=inv_brief_data.net_total,
        tax_total=inv_brief_data.tax_total,
        gross_total=inv_brief_data.gross_total,
        payment=InvoicePayment(
            payment_status=inv_payment_data.payment_status,
            payment_type=inv_payment_data.payment_type,
            payment_date=inv_payment_data.payment_date
            if inv_payment_data.payment_date
            else None,
            payment_due_date=inv_payment_data.payment_due_date
            if inv_payment_data.payment_due_date
            else None,
            partial_payments=inv_payment_data.partial_payments,
            seller_bank_account_number=inv_payment_data.seller_bank_account_number,
            seller_bank_name=inv_payment_data.seller_bank_name,
        )
        if inv_payment_data
        else None,
        annotations=inv_detailed_data.annotation,
        additional_info=inv_detailed_data.additional_info,
        footer_info=inv_detailed_data.footer_info,
        footer_registers=inv_detailed_data.footer_registers,
    )
