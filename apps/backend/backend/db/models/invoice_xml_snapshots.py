from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import uuid4

from backend.db.base import Base


class InvoiceXmlSnapshotsTable(Base):
    """Table containing Invoices in XML format."""

    __tablename__ = "invoice_xml_snapshots"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    invoice_id: Mapped[str] = mapped_column(
        String, ForeignKey("invoices_brief.id"), nullable=False
    )

    xml: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    sha256_base64: Mapped[str] = mapped_column(String, nullable=True, unique=True)

    invoice = relationship("InvoicesBriefTable", back_populates="invoice_xml_snapshots")
