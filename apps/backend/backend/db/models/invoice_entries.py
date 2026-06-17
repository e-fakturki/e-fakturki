from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.db.base import Base


class InvoiceEntriesTable(Base):
    """
    Table containing invoice entries (sold products/services list).
    Not all fields from the FA (3) XML structure are covered.
    """

    __tablename__ = "invoice_entries"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    invoice_id: Mapped[str] = mapped_column(
        String, ForeignKey("invoices_brief.id"), nullable=False
    )

    row_number: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="FA (3) Faktura.fa.faWiersz.nr_wiersza_fa"
    )
    uu_id: Mapped[str] = mapped_column(
        String, nullable=True, comment="KSeF assigned unique row uuid."
    )
    gtin: Mapped[str] = mapped_column(
        String, nullable=True, comment="FA (3) Faktura.fa.faWiersz.gtin"
    )
    delivery_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, comment="FA (3) Faktura.fa.faWiersz.p_6_a"
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="FA (3) Faktura.fa.faWiersz.p_7"
    )
    index: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="Internal product code or desc."
    )
    unit: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="FA (3) Faktura.fa.faWiersz.p_8_a"
    )
    amount: Mapped[float] = mapped_column(
        Float, nullable=False, comment="FA (3) Faktura.fa.faWiersz.p_8_b"
    )

    net_price: Mapped[float] = mapped_column(
        Float, nullable=True, comment="FA (3) Faktura.fa.faWiersz.p_9_a"
    )
    gross_price: Mapped[float] = mapped_column(
        Float, nullable=True, comment="FA (3) Faktura.fa.faWiersz.p_9_b"
    )
    discount: Mapped[float] = mapped_column(
        Float, nullable=True, comment="FA (3) Faktura.fa.faWiersz.p_10"
    )
    net_total: Mapped[float] = mapped_column(
        Float, nullable=True, comment="FA (3) Faktura.fa.faWiersz.p_11"
    )
    gross_total: Mapped[float] = mapped_column(
        Float, nullable=True, comment="FA (3) Faktura.fa.faWiersz.p_11_a"
    )

    tax_total: Mapped[float] = mapped_column(
        Float, nullable=True, comment="FA (3) Faktura.fa.faWiersz.p_11_vat"
    )
    tax_rate: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="FA (3) Faktura.fa.faWiersz.p_12"
    )

    invoice = relationship("InvoicesBriefTable", back_populates="invoice_entries")
