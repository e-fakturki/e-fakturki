from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import uuid4

from backend.db.base import Base


class InvoiceDetailsTable(Base):
    """
    Table containing invoices details,
    ingested from single invoice download KSeF API endpoint.
    Not all fields from the FA (3) XML structure are covered.
    """

    __tablename__ = "invoice_details"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    invoice_id: Mapped[str] = mapped_column(
        String, ForeignKey("invoices_brief.id"), nullable=False
    )
    form_code: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="FA (3) Faktura.naglowek.kod_formularza"
    )

    system_info: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="FA (3) Faktura.naglowek.system_info"
    )

    issue_place: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="FA (3) Faktura.fa.p_1_m"
    )

    seller_address_l1: Mapped[str] = mapped_column(
        Text, nullable=True, comment="FA (3) Faktura.podmiot1.adres.adres_l1"
    )
    seller_address_l2: Mapped[str] = mapped_column(
        Text, nullable=True, comment="FA (3) Faktura.podmiot1.adres.adres_l2"
    )
    seller_email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="FA (3) Faktura.podmiot1.dane_kontaktowe.email",
    )
    seller_phone: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="FA (3) Faktura.podmiot1.dane_kontaktowe.telefon",
    )

    buyer_address_l1: Mapped[str] = mapped_column(
        Text, nullable=True, comment="FA (3) Faktura.podmiot2.adres.adres_l1"
    )
    buyer_address_l2: Mapped[str] = mapped_column(
        Text, nullable=True, comment="FA (3) Faktura.podmiot2.adres.adres_l2"
    )
    buyer_email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="FA (3) Faktura.podmiot1.dane_kontaktowe.email",
    )
    buyer_phone: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="FA (3) Faktura.podmiot2.dane_kontaktowe.telefon",
    )

    annotation: Mapped[str] = mapped_column(
        Text, nullable=True, comment="FA (3) Faktura.fa.adnotacje"
    )
    additional_info: Mapped[str] = mapped_column(
        Text, nullable=True, comment="FA (3) Faktura.fa.dodatkowy_opis"
    )

    footer_info: Mapped[str] = mapped_column(
        Text, nullable=True, comment="FA (3) Faktura.stopka.informacje"
    )
    footer_registers: Mapped[str] = mapped_column(
        Text, nullable=True, comment="FA (3) Faktura.stopka.rejestry"
    )

    invoice = relationship("InvoicesBriefTable", back_populates="invoice_details")
