from datetime import datetime
from backend.db.models.invoice_details import InvoiceDetailsTable
import backend.domain.fa3_xml_utils.models.schemat as fa3utils


def parse_date(value: str | None) -> datetime | None:
    """Convert ISO string to datetime, or return None if empty."""
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def map_fa3_to_invoice_details_table(
    fa3: fa3utils.Faktura, invoice_id: str
) -> InvoiceDetailsTable:
    """Map FA3 dataclass fields to InvoiceTable db schema fields."""
    return InvoiceDetailsTable(
        invoice_id=invoice_id,
        form_code=str(fa3.naglowek.kod_formularza),
        system_info=fa3.naglowek.system_info,
        ###
        issue_place=fa3.fa.p_1_m,
        ###
        seller_address_l1=fa3.podmiot1.adres.adres_l1,
        seller_address_l2=fa3.podmiot1.adres.adres_l2,
        seller_email=fa3.podmiot1.dane_kontaktowe[0].email
        if fa3.podmiot1.dane_kontaktowe
        else None,
        seller_phone=fa3.podmiot1.dane_kontaktowe[0].telefon
        if fa3.podmiot1.dane_kontaktowe
        else None,
        ###
        buyer_address_l1=fa3.podmiot2.adres.adres_l1
        if fa3.podmiot2.adres.adres_l1
        else None,
        buyer_address_l2=fa3.podmiot2.adres.adres_l2
        if fa3.podmiot2.adres.adres_l2
        else None,
        buyer_email=fa3.podmiot2.dane_kontaktowe[0].email
        if fa3.podmiot2.dane_kontaktowe
        else None,
        buyer_phone=fa3.podmiot2.dane_kontaktowe[0].telefon
        if fa3.podmiot2.dane_kontaktowe
        else None,
        ###
        annotation=str(fa3.fa.adnotacje) if fa3.fa.adnotacje else None,
        additional_info=str(fa3.fa.dodatkowy_opis) if fa3.fa.dodatkowy_opis else None,
        ###
        footer_info=fa3.stopka.informacje[0].stopka_faktury
        if (fa3.stopka and fa3.stopka.informacje)
        else None,
        footer_registers=str(fa3.stopka.rejestry)
        if (fa3.stopka and fa3.stopka.rejestry)
        else None,
    )
