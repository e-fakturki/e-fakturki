from enum import Enum as PyEnum

from datetime import datetime
from sqlalchemy import DateTime, Enum, Numeric, String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import uuid4

from backend.db.base import Base


class KsefStatus(PyEnum):
    """Statuses of an invoice in the ksef system."""

    not_sent = "not_sent"
    sent = "sent"
    acc = "accepted"
    rej = "rejected"


class InvoicesBriefTable(Base):
    """
    Table containing brief info about invoices,
    ingested from invoice metadata list KSeF API endpoint.
    """

    __tablename__ = "invoices_brief"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )

    ksef_number: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    invoice_number: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    issue_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )
    invoicing_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    acquisition_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    permanent_storage_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    ksef_status: Mapped[str] = mapped_column(
        Enum(KsefStatus, name="ksef_status"),
        nullable=False,
        default=KsefStatus.not_sent,
    )

    seller_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    seller_nip: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    buyer_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    buyer_nip: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    net_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    gross_total: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, index=False
    )
    tax_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(255), nullable=False)

    invoicing_mode: Mapped[str] = mapped_column(String(255), nullable=True)
    invoice_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    has_attachment: Mapped[bool] = mapped_column(Boolean, nullable=True)

    is_new: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )

    invoice_details = relationship("InvoiceDetailsTable", back_populates="invoice")

    invoice_entries = relationship("InvoiceEntriesTable", back_populates="invoice")

    invoices_payment_details = relationship(
        "InvoicesPaymentTable", back_populates="invoice"
    )

    invoice_xml_snapshots = relationship(
        "InvoiceXmlSnapshotsTable", back_populates="invoice"
    )
