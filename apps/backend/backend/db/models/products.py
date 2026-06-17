from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, String, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import uuid4

from backend.db.base import Base
from backend.domain.fa3_xml_utils.models.schemat import TstawkaPodatku


tax_rates_descriptions: dict[str, str] = {
    TstawkaPodatku.VALUE_23.value: "VAT 23%",
    TstawkaPodatku.VALUE_22.value: "VAT 22%",
    TstawkaPodatku.VALUE_8.value: "VAT 8%",
    TstawkaPodatku.VALUE_7.value: "VAT 7%",
    TstawkaPodatku.VALUE_5.value: "VAT 5%",
    TstawkaPodatku.VALUE_4.value: "VAT 4%",
    TstawkaPodatku.VALUE_3.value: "VAT 3%",
    TstawkaPodatku.VALUE_0_KR.value: "VAT 0% w przypadku sprzedaży towarów i świadczenia usług na terytorium kraju (z wyłączeniem WDT i eksportu)",
    TstawkaPodatku.VALUE_0_WDT.value: "VAT 0% w przypadku wewnątrzwspólnotowej dostawy towarów (WDT)",
    TstawkaPodatku.VALUE_0_EX.value: "VAT 0% w przypadku eksportu towarów",
    TstawkaPodatku.ZW.value: "Towary zwolnione od podatku",
    TstawkaPodatku.OO.value: "Odwrotne obciążenie",
    TstawkaPodatku.NP_I.value: "Towary niepodlegające opodatkowaniu- dostawy towarów oraz świadczenia usług poza terytorium kraju, z wyłączeniem transakcji, o których mowa w art. 100 ust. 1 pkt 4 ustawy oraz OSS",
    TstawkaPodatku.NP_II.value: "Towary niepodlegajace opodatkowaniu na terytorium kraju, świadczenie usług o których mowa w art. 100 ust. 1 pkt 4 ustawy",
}

tax_rate_values: dict[str, float] = {
    TstawkaPodatku.VALUE_23.value: 0.23,
    TstawkaPodatku.VALUE_22.value: 0.22,
    TstawkaPodatku.VALUE_8.value: 0.08,
    TstawkaPodatku.VALUE_7.value: 0.07,
    TstawkaPodatku.VALUE_5.value: 0.05,
    TstawkaPodatku.VALUE_4.value: 0.04,
    TstawkaPodatku.VALUE_3.value: 0.03,
    TstawkaPodatku.VALUE_0_KR.value: 0,
    TstawkaPodatku.VALUE_0_WDT.value: 0,
    TstawkaPodatku.VALUE_0_EX.value: 0,
    TstawkaPodatku.ZW.value: 0,
    TstawkaPodatku.OO.value: 0,
    TstawkaPodatku.NP_I.value: 0,
    TstawkaPodatku.NP_II.value: 0,
}

tax_rates_display: dict[str, str] = {
    TstawkaPodatku.VALUE_23.value: "VAT 23%",
    TstawkaPodatku.VALUE_22.value: "VAT 22%",
    TstawkaPodatku.VALUE_8.value: "VAT 8%",
    TstawkaPodatku.VALUE_7.value: "VAT 7%",
    TstawkaPodatku.VALUE_5.value: "VAT 5%",
    TstawkaPodatku.VALUE_4.value: "VAT 4%",
    TstawkaPodatku.VALUE_3.value: "VAT 3%",
    TstawkaPodatku.VALUE_0_KR.value: "VAT 0% (KR)",
    TstawkaPodatku.VALUE_0_WDT.value: "VAT 0% (WDT)",
    TstawkaPodatku.VALUE_0_EX.value: "VAT 0% (EX)",
    TstawkaPodatku.ZW.value: "VAT 0% (ZW)",
    TstawkaPodatku.OO.value: "Odwrotne obciążenie",
    TstawkaPodatku.NP_I.value: "VAT 0% (NP I)",
    TstawkaPodatku.NP_II.value: "VAT 0% (NP II)",
}


class ProductsTable(Base):
    """Table containing products."""

    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)

    name: Mapped[str] = mapped_column(
        String(512), nullable=False, comment="FA (3) Faktura.fa.faWiersz.p_7"
    )
    description: Mapped[str] = mapped_column(
        String(2048), nullable=True, comment="Internal product code or desc."
    )
    gtin: Mapped[str] = mapped_column(
        String(20), nullable=True, comment="FA (3) Faktura.fa.faWiersz.gtin"
    )

    unit: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="FA (3) Faktura.fa.faWiersz.p_8_a"
    )

    net_price: Mapped[float] = mapped_column(Float, nullable=True)
    tax_rate: Mapped[str] = mapped_column(
        Enum(TstawkaPodatku, name="tax_rate"),
        nullable=True,
        default=None,
        comment="FA (3) Faktura.fa.faWiersz.p_12",
    )
    gross_price: Mapped[float] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    company = relationship("CompaniesTable", back_populates="products")
