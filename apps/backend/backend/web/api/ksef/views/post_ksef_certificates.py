from sqlite3 import IntegrityError

from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.web.api.ksef.services import decrypt_ksef_certs
from backend.schemas.auth import UserRead
from backend.web.api.auth.services import get_current_user
from backend.schemas.ksef import CredentialsCreateResponse, KsefCertificatesLoad
from backend.db.dependencies import get_db_session
from backend.db.repositories.ksef_credentials_repository import (
    get_auth_certs,
    insert_new_ksef_credentials,
)
from backend.services.encryptor import Encryptor

router = APIRouter()


@router.post("/certificates", status_code=201, response_model=CredentialsCreateResponse)
async def upload_ksef_certificates(
    company_id: str = Form(
        ..., description="The ID of the company to which the certificates belong."
    ),
    online_certificates: bool = Form(
        ...,
        description="Whether the uploaded certificates are for authentication (True) or for offline mode (False).",
    ),
    certificate: UploadFile = File(
        ..., description="The certificate file to be uploaded."
    ),
    private_key: UploadFile = File(
        ..., description="The private key file to be uploaded."
    ),
    password: str = Form(..., description="The password for the private key."),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> CredentialsCreateResponse:
    """Uploads KSeF certificates for a company to the database."""

    # encrypt the ksef credentials before saving to db
    encrypted_cert_content = Encryptor().encrypt_bytes(await certificate.read())
    encrypted_private_key_content = Encryptor().encrypt_bytes(await private_key.read())
    encrypted_password = Encryptor().encrypt_text(password)

    try:
        return await insert_new_ksef_credentials(
            db=db_session,
            company_id=company_id,
            certificate_content=encrypted_cert_content,
            private_key_content=encrypted_private_key_content,
            private_key_password=encrypted_password,
            online_certificates=online_certificates,
        )

    except IntegrityError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/certificates/{company_id}", status_code=200)
async def get_ksef_certificates(
    company_id: str = Path(
        ..., description="The ID of the company to which the certificates belong."
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> KsefCertificatesLoad:
    """Get KSeF certificates for a company."""

    try:
        certificates = await get_auth_certs(db_session, company_id)

        return decrypt_ksef_certs(certificates)

    except IntegrityError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
