import backend.domain.fa3_xml_utils.models.schemat as fa3utils
from backend.db.models.invoices_payment import (
    InvoicesPaymentTable,
    PaymentStatus,
    PaymentType,
)
from backend.db.mappings.invoice_details_mappings import parse_date


def parse_payment_type(
    fa3_fa_platnosc_forma_platnosci: list[
        fa3utils.TformaPlatnosci | fa3utils.Twybor1 | str
    ],
) -> PaymentType | None:
    """Extract payment type from FA3.Faktura.Fa.Platnosc.forma_platnosci_or_platnosc_inna_or_opis_platnosci"""
    if len(fa3_fa_platnosc_forma_platnosci) == 0:
        return None
    if isinstance(fa3_fa_platnosc_forma_platnosci[0], fa3utils.TformaPlatnosci):
        return PaymentType(fa3_fa_platnosc_forma_platnosci[0].value)
    return None


def parse_payment_status(
    fa3_fa_platnosc_choice: list[
        fa3utils.Twybor1
        | str
        | fa3utils.Twybor12
        | fa3utils.Faktura.Fa.Platnosc.ZaplataCzesciowa
    ],
) -> PaymentStatus | None:
    """Extract payment status from FA3.Faktura.Fa.Platnosc.Choice"""
    if len(fa3_fa_platnosc_choice) == 0:
        return PaymentStatus.unpaid
    if type(fa3_fa_platnosc_choice[0]) in [fa3utils.Twybor1, str]:
        return PaymentStatus.paid
    if type(fa3_fa_platnosc_choice[0]) in [
        fa3utils.Twybor12,
        fa3utils.Faktura.Fa.Platnosc.ZaplataCzesciowa,
    ]:
        return PaymentStatus.partial
    return None


def parse_payment_date(
    fa3_fa_platnosc_choice: list[
        fa3utils.Twybor1
        | str
        | fa3utils.Twybor12
        | fa3utils.Faktura.Fa.Platnosc.ZaplataCzesciowa
    ],
) -> str | None:
    """Extract payment date from FA3.Faktura.Fa.Platnosc.Choice"""
    if len(fa3_fa_platnosc_choice) == 0:
        return None
    if type(fa3_fa_platnosc_choice[0]) in [fa3utils.Twybor1, str]:
        for item in fa3_fa_platnosc_choice:
            if isinstance(item, str):
                return parse_date(item)
    if type(fa3_fa_platnosc_choice[0]) in [
        fa3utils.Twybor12,
        fa3utils.Faktura.Fa.Platnosc.ZaplataCzesciowa,
    ]:
        return None
    return None


def parse_partial_payments(
    fa3_fa_platnosc_choice: list[
        fa3utils.Twybor1
        | str
        | fa3utils.Twybor12
        | fa3utils.Faktura.Fa.Platnosc.ZaplataCzesciowa
    ],
) -> list[list[float | str]] | None:
    """Extract partial payments data from FA3.Faktura.Fa.Platnosc.Choice"""
    partial_payments = []

    if len(fa3_fa_platnosc_choice) == 0:
        return None
    if type(fa3_fa_platnosc_choice[0]) in [fa3utils.Twybor1, str]:
        return None
    if type(fa3_fa_platnosc_choice[0]) in [
        fa3utils.Twybor12,
        fa3utils.Faktura.Fa.Platnosc.ZaplataCzesciowa,
    ]:
        for item in fa3_fa_platnosc_choice:
            if isinstance(item, fa3utils.Faktura.Fa.Platnosc.ZaplataCzesciowa):
                partial_payments.append(
                    [item.data_zaplaty_czesciowej, item.kwota_zaplaty_czesciowej]
                )
        return partial_payments
    return None


def map_fa3_fa_platnosc_to_invoices_payment_table(
    fa3: fa3utils.Faktura.Fa.Platnosc, invoice_id: str
) -> InvoicesPaymentTable:
    """Map FA3 dataclass fields to InvoicePaymentTable db schema fields."""
    return InvoicesPaymentTable(
        invoice_id=invoice_id,
        payment_type=parse_payment_type(
            fa3.forma_platnosci_or_platnosc_inna_or_opis_platnosci
        )
        if (
            fa3.forma_platnosci_or_platnosc_inna_or_opis_platnosci
            and len(fa3.forma_platnosci_or_platnosc_inna_or_opis_platnosci) > 0
        )
        else None,
        payment_due_date=parse_date(fa3.termin_platnosci[0].termin)
        if (fa3.termin_platnosci and len(fa3.termin_platnosci) > 0)
        else None,
        payment_status=parse_payment_status(fa3.choice),
        payment_date=parse_payment_date(fa3.choice),
        partial_payments=parse_partial_payments(fa3.choice),
        seller_bank_account_number=fa3.rachunek_bankowy[0].nr_rb
        if (fa3.rachunek_bankowy and len(fa3.rachunek_bankowy) > 0)
        else None,
        seller_bank_name=fa3.rachunek_bankowy[0].nazwa_banku
        if (fa3.rachunek_bankowy and len(fa3.rachunek_bankowy) > 0)
        else None,
    )
