from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import uuid4


from backend.db.base import Base


class CompaniesTable(Base):
    """Table containing companies."""

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    nip: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    regon: Mapped[str] = mapped_column(String(14), nullable=True, unique=True)
    krs: Mapped[str] = mapped_column(String(10), nullable=True, unique=True)

    country_code: Mapped[str] = mapped_column(String(16), nullable=True)
    address_l1: Mapped[str] = mapped_column(String(512), nullable=True)
    address_l2: Mapped[str] = mapped_column(String(512), nullable=True)
    address_correspondance_l1: Mapped[str] = mapped_column(String(512), nullable=True)
    address_correspondance_l2: Mapped[str] = mapped_column(String(512), nullable=True)

    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    additional_info: Mapped[str] = mapped_column(String(2048), nullable=True)

    iban: Mapped[str] = mapped_column(String(36), nullable=True)
    bank_name: Mapped[str] = mapped_column(String(255), nullable=True)
    swift: Mapped[str] = mapped_column(String(10), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("UsersTable", back_populates="companies")
    products = relationship("ProductsTable", back_populates="company")
    ksef_credentials = relationship("KsefCredentialsTable", back_populates="company")
