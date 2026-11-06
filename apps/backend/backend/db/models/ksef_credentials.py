from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Text, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import uuid4

from backend.db.base import Base


class KsefCredentialsTable(Base):
    """Table containing KSeF credentials for a company (certificates, passwords, private keys, tokens)."""

    __tablename__ = "ksef_credentials"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        String, ForeignKey("companies.id"), nullable=False
    )

    cert_auth: Mapped[str] = mapped_column(Text, nullable=False)
    private_key_auth: Mapped[str] = mapped_column(Text, nullable=False)
    password_auth: Mapped[str] = mapped_column(Text, nullable=False)
    cert_offline: Mapped[str] = mapped_column(Text, nullable=True)
    private_key_offline: Mapped[str] = mapped_column(Text, nullable=True)
    password_offline: Mapped[str] = mapped_column(Text, nullable=True)
    token: Mapped[str] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    company = relationship("CompaniesTable", back_populates="ksef_credentials")
