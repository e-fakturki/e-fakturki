from sqlite3 import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.ksef import CredentialsCreateResponse
from backend.db.models.ksef_credentials import KsefCredentialsTable
from backend.schemas.ksef import KsefCertificatesLoad


async def insert_new_ksef_credentials(
    db: AsyncSession,
    company_id: str,
    certificate_content: str | bytes,
    private_key_content: str | bytes,
    private_key_password: str | bytes,
    online_certificates: bool,
) -> CredentialsCreateResponse | None:
    """Insert a new set of KSeF credentials into the database."""
    try:
        credentials = KsefCredentialsTable(
            company_id=company_id,
            cert_auth=certificate_content if online_certificates else None,
            private_key_auth=private_key_content if online_certificates else None,
            password_auth=private_key_password if online_certificates else None,
            cert_offline=certificate_content if not online_certificates else None,
            private_key_offline=private_key_content
            if not online_certificates
            else None,
            password_offline=private_key_password if not online_certificates else None,
            token=None,
            token_expires_at=None,
        )
        db.add(credentials)
        await db.commit()
        await db.refresh(credentials)

        return CredentialsCreateResponse(
            company_id=credentials.company_id, credentials_id=credentials.id
        )

    except IntegrityError:
        await db.rollback()
        raise


async def get_ksef_credentials(
    db: AsyncSession, company_id: str
) -> KsefCredentialsTable | None:
    """Get the KSeF credentials for the company with given ID."""
    stmt = (
        select(KsefCredentialsTable)
        .where(KsefCredentialsTable.company_id == company_id)
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_auth_certs(
    db_session: AsyncSession, company_id: str
) -> KsefCertificatesLoad:
    """Loads cert, private_key and private_key_password from the database."""
    stmt = (
        select(
            KsefCredentialsTable.cert_auth,
            KsefCredentialsTable.private_key_auth,
            KsefCredentialsTable.password_auth,
        )
        .where(KsefCredentialsTable.company_id == company_id)
        .limit(1)
    )

    result = await db_session.execute(stmt)
    row = result.first()

    if row is None:
        raise ValueError(f"Certificates not found for (company_id={company_id})")

    cert, key, password = row

    return KsefCertificatesLoad(
        certificate=cert,
        private_key=key,
        password=password,
    )
