from backend.db.models.invoice_entries import InvoiceEntriesTable
from backend.db.mappings.invoice_details_mappings import parse_date
import backend.domain.fa3_xml_utils.models.schemat as fa3utils


def parse_tax_rate(tax_rate: fa3utils.TstawkaPodatku) -> int:
    """
    Convert FA3 tax rate to int - local db field type.
    The fa3utils.TstawkaPodatku can contain different values,
    """
    if tax_rate is None:
        return 0
    try:
        return int(tax_rate)
    except ValueError:
        return 0


def map_fa3_fawiersz_to_invoice_entries_table(
    fa3: fa3utils.Faktura.Fa.FaWiersz, invoice_id: str
) -> InvoiceEntriesTable:
    """Map FA3 dataclass fields to InvoiceEntriesTable db schema fields."""
    return InvoiceEntriesTable(
        invoice_id=invoice_id,
        row_number=fa3.nr_wiersza_fa,
        uu_id=fa3.uu_id,
        gtin=fa3.gtin,
        delivery_date=parse_date(fa3.p_6_a),
        name=fa3.p_7,
        index=fa3.indeks if fa3.indeks else None,
        unit=fa3.p_8_a,
        amount=fa3.p_8_b,  # here string in db float
        net_price=fa3.p_9_a,  # here string in db float
        gross_price=fa3.p_9_b,  # here string in db float
        discount=fa3.p_10,  # here string in db float
        net_total=fa3.p_11,  # here string in db float
        gross_total=fa3.p_11_a,  # here string in db float
        tax_total=fa3.p_11_vat,  # here string in db float
        tax_rate=parse_tax_rate(fa3.p_12.value),
    )
