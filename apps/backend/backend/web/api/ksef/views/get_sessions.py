from fastapi import APIRouter, Depends, HTTPException, Path
from ksef_client import KsefClient, KsefClientOptions, models as m
from ksef_client.exceptions import KsefRateLimitError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.web.api.ksef.services import decrypt_ksef_certs
from backend.db.dependencies import get_db_session
from backend.db.repositories.company_repository import get_company_nip
from backend.services.ksef.auth.certificate_auth import (
    authorize_ksef_with_certificate,
    certificate_str_to_temp_file,
    remove_temp_file,
)
from backend.schemas.auth import UserRead
from backend.web.api.auth.services import get_current_user
from backend.services.ksef.auth.ksef_session import open_ksef_session
from backend.db.repositories.ksef_credentials_repository import get_auth_certs

from backend.settings import Settings

router = APIRouter()


@router.post("/{company_id}/active-sessions", status_code=200)
async def get_invoices_list(
    company_id: str = Path(
        ..., description="The ID of the company for session filtering."
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[m.SessionsQueryResponseItem]:
    """Get the list of KSeF sessions."""

    # load needed company data for the upload, including NIP and certs
    company_nip = await get_company_nip(db_session, company_id)
    company_ksef_certs = decrypt_ksef_certs(
        await get_auth_certs(db_session, company_id)
    )
    password = company_ksef_certs.password
    cert_path = certificate_str_to_temp_file(company_ksef_certs.certificate)
    key_path = certificate_str_to_temp_file(company_ksef_certs.private_key)

    with KsefClient(KsefClientOptions(base_url=Settings.ksef_environment())) as client:
        sym_cert = client.security.get_public_key_certificate_pem(
            m.PublicKeyCertificateUsage.SYMMETRICKEYENCRYPTION,
        )
        try:
            # authenticate with certs
            access_token = (
                authorize_ksef_with_certificate(
                    certificate_path=cert_path,
                    private_key_path=key_path,
                    private_key_password=password,
                    client=client,
                    context_id_value=company_nip,
                )
            ).tokens.access_token.token

            ksef_session_params = open_ksef_session(
                client=client, access_token=access_token, sym_cert=sym_cert
            )
            sessions_metadata = client.sessions.get_sessions(
                session_type="Online",
                statuses=["InProgress"],
                page_size=1000,
                access_token=access_token,
            )
        except KsefRateLimitError as e:
            raise HTTPException(
                status_code=429,
                detail="Przekroczono limit 20 żądań na minutę w KSeF. Spróbuj ponownie po 30 sekundach.",
            ) from e
        except Exception:
            raise
        finally:
            if ksef_session_params is not None:
                ksef_session_params.workflow.close_session(
                    ksef_session_params.session.session_reference_number, access_token
                )
                remove_temp_file(cert_path)
                remove_temp_file(key_path)

    return sessions_metadata.sessions
