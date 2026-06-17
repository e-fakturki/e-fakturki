from enum import Enum as PyEnum

from datetime import datetime
from sqlalchemy import DateTime, Enum, String, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import uuid4

from backend.db.base import Base


class PaymentType(PyEnum):
    """Types of payment."""

    cash = 1
    card = 2
    bon = 3
    cheque = 4
    loan = 5
    transfer = 6
    mobile = 7


class PaymentStatus(PyEnum):
    """Statuses of an invoice."""

    unpaid = "unpaid"
    partial = "partial"
    paid = "paid"


class InvoicesPaymentTable(Base):
    """
    Table containing invoices payment details,
    ingested from single invoice download KSeF API endpoint.
    """

    __tablename__ = "invoices_payment_details"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    invoice_id: Mapped[str] = mapped_column(
        String, ForeignKey("invoices_brief.id"), nullable=False
    )

    payment_type: Mapped[str] = mapped_column(
        Enum(PaymentType, name="payment_type"),
        nullable=True,
        default=None,
        comment="FA (3) Faktura.fa.platnosc.forma_platnosci_or_platnosc_inna_or_opis_platnosci",
    )
    payment_due_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="FA (3) Faktura.fa.platnosc.termin_platnosci"
    )
    payment_status: Mapped[str] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        nullable=False,
        default=PaymentStatus.unpaid,
        comment="FA (3) Faktura.fa.platnosc.choice(fa3utils.Twybor1.VALUE_1 | fa3utils.Twybor12.VALUE_2)",
    )
    payment_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="FA (3) Faktura.fa.platnosc.choice(str)"
    )
    partial_payments: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="FA (3) Faktura.fa.platnosc.choice(fa3utils.Faktura.Fa.Platnosc.ZaplataCzesciowa)",
    )
    seller_bank_account_number: Mapped[list[list[float | str]]] = mapped_column(
        Text,
        nullable=True,
        comment="FA (3) Faktura.podmiot1.platnosc.rachunek_bankowy.nr_rb",
    )
    seller_bank_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="FA (3) Faktura.podmiot1.platnosc.nazwa_banku",
    )

    invoice = relationship(
        "InvoicesBriefTable", back_populates="invoices_payment_details"
    )
