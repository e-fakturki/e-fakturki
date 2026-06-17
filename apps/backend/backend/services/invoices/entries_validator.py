from math import isclose

from backend.schemas.invoices import InvoiceResponse
from backend.db.repositories.invoices_entries_repository import InvoiceEntry

MONEY_TOLERANCE = 0.005


def validate_invoice_entry(entry: InvoiceEntry) -> None:
    """Validate a single invoice entry."""

    if (
        entry.net_price is None
        or entry.net_total is None
        or entry.tax_total is None
        or entry.gross_total is None
    ):
        return

    expected_net_total = entry.net_price * entry.amount

    if not isclose(
        expected_net_total,
        entry.net_total,
        abs_tol=MONEY_TOLERANCE,
    ):
        raise ValueError(
            f"Entry {entry.row_number}: "
            f"net_price * amount = {expected_net_total:.2f}, "
            f"but net_total = {entry.net_total:.2f}"
        )

    expected_tax_total = entry.net_total * (entry.tax_rate / 100)

    if not isclose(
        expected_tax_total,
        entry.tax_total,
        abs_tol=MONEY_TOLERANCE,
    ):
        raise ValueError(
            f"Entry {entry.row_number}: "
            f"expected tax_total = {expected_tax_total:.2f}, "
            f"but tax_total = {entry.tax_total:.2f}"
        )

    expected_gross_total = entry.net_total + entry.tax_total

    if not isclose(
        expected_gross_total,
        entry.gross_total,
        abs_tol=MONEY_TOLERANCE,
    ):
        raise ValueError(
            f"Entry {entry.row_number}: "
            f"expected gross_total = {expected_gross_total:.2f}, "
            f"but gross_total = {entry.gross_total:.2f}"
        )


def validate_invoice_totals(invoice: InvoiceResponse) -> None:
    """Validate invoice totals against entries."""

    net_total = sum(entry.net_total or 0 for entry in invoice.entries)
    tax_total = sum(entry.tax_total or 0 for entry in invoice.entries)
    gross_total = sum(entry.gross_total or 0 for entry in invoice.entries)

    if not isclose(net_total, invoice.net_total, abs_tol=MONEY_TOLERANCE):
        raise ValueError(
            f"Entries net total ({net_total:.2f}) "
            f"does not match invoice net total ({invoice.net_total:.2f})"
        )

    if not isclose(tax_total, invoice.tax_total, abs_tol=MONEY_TOLERANCE):
        raise ValueError(
            f"Entries tax total ({tax_total:.2f}) "
            f"does not match invoice tax total ({invoice.tax_total:.2f})"
        )

    if not isclose(gross_total, invoice.gross_total, abs_tol=MONEY_TOLERANCE):
        raise ValueError(
            f"Entries gross total ({gross_total:.2f}) "
            f"does not match invoice gross total ({invoice.gross_total:.2f})"
        )
