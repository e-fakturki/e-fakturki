import asyncio
from typing import Any

from ksef_client import KsefClient

from backend.services.ksef.auth.ksef_session import KsefSessionParams
import time

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from ksef_client import KsefClientOptions, models as m
from ksef_client.exceptions import KsefRateLimitError
from backend.web.api.ksef.services import decrypt_ksef_certs
from backend.db.repositories.company_repository import get_company_nip
from backend.services.ksef.auth.certificate_auth import (
    authorize_ksef_with_certificate,
    certificate_str_to_temp_file,
    remove_temp_file
    )
from backend.services.ksef.auth.ksef_session import open_ksef_session
from backend.schemas.ksef import KsefInvoiceUploadStatus
from backend.db.repositories.ksef_credentials_repository import get_auth_certs

from backend.settings import Settings


def single_invoice_upload(
    ksef_session_params: KsefSessionParams,
    access_token: str,
    invoice_xml: bytes,
    offline_mode: bool | None = None,
    hash_of_corrected_invoice: str | None = None,
) -> Any:
    """
    Uploads XML of the invoice to KSEF API.

    Args:
        ksef_session_params: Parameters needed to run a ksef session.
        access_token: Access token for authentication.
        invoice_xml: XML string of the invoice to be uploaded.
        offline_mode: Whether to upload in offline mode.
        hash_of_corrected_invoice: Only if the invoice is a correction.

    Returns:
        An object containing the results of the upload, including the reference number.

    Todo:
        * handle errors statuses returned from the API.
    """
    return ksef_session_params.workflow.send_invoice(
        session_reference_number=ksef_session_params.session.session_reference_number,
        invoice_xml=invoice_xml,
        encryption_data=ksef_session_params.session.encryption_data,
        access_token=access_token,
        offline_mode=offline_mode,
        hash_of_corrected_invoice=hash_of_corrected_invoice,
    )


async def check_upload_status(
    client: KsefClient,
    ksef_session_params: KsefSessionParams,
    access_token: str,
    invoice_reference_number: str,
) -> Any:
    """
    Checks the status of the uploaded invoice in KSEF API.

    Runs in a loop until the status is no longer "processing",
    or "accepted for processing" or until timeout.

    Args:
        client: An instance of KsefClient.
        ksef_session_params: Parameters needed to run a ksef session.
        access_token: Access token for authentication.
        invoice_reference_number: Reference number of the uploaded invoice.

    Returns:
        An object containing the status of the uploaded invoice.
    """
    for _ in range(60):
        status = client.sessions.get_session_invoice_status(
            ksef_session_params.session.session_reference_number,
            invoice_reference_number,
            access_token=access_token,
        )

        code = int(status.get("status", {}).get("code", 0))

        if code == 200:
            return status
        if code not in {100, 150}:
            return status

        await asyncio.sleep(2)

    raise TimeoutError("Invoice upload status check timeout.")


async def post_invoice_to_ksef(db_session: AsyncSession, company_id: str, xml: bytes) -> KsefInvoiceUploadStatus:
    """Post invoice to KSEF."""
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

            send_result = ksef_session_params.session.send_invoice(
                invoice_xml=xml,
                access_token=access_token,
            )

            invoice_reference = send_result.reference_number

            status = None
            for _ in range(60):
                status = ksef_session_params.session.get_invoice_status(invoice_reference, access_token=access_token)
                code = int(status.status.code)
                if code == 200:
                    break
                if code not in {100, 150}:
                    raise RuntimeError(status.to_dict())
                time.sleep(2)

        except KsefRateLimitError as e:
            raise HTTPException(
                status_code=429,
                detail="Przekroczono limit 20 żądań na minutę w KSeF. Spróbuj ponownie po 30 sekundach.",
            ) from e
        except Exception as e:
            raise
        finally:
            if ksef_session_params is not None:
                ksef_session_params.workflow.close_session(
                    ksef_session_params.session.session_reference_number, access_token
                )
                remove_temp_file(cert_path)
                remove_temp_file(key_path)

    return KsefInvoiceUploadStatus(
        company_id=company_id,
        invoice_id=1,
        ksef_status=status.status.code,
        ksef_reference_number=invoice_reference,
    )
