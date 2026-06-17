import time

from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.fa3_xml_utils.utils.parser import FA3XmlParser
from backend.domain.fa3_xml_utils.utils.builder import FA3XmlBuilder
from backend.db.repositories.invoice_xml_repository import get_invoice_xml
from fastapi import HTTPException
from ksef_client import KsefClient, KsefClientOptions, models as m
from ksef_client.exceptions import KsefRateLimitError
from backend.web.api.ksef.services import decrypt_ksef_certs
from backend.db.repositories.company_repository import get_company_nip
from backend.services.ksef.auth.certificate_auth import (
    authorize_ksef_with_certificate,
    certificate_str_to_temp_file,
    remove_temp_file,)
from backend.services.ksef.auth.ksef_session import open_ksef_session
from backend.services.ksef.invoicing.upload import (
    check_upload_status,
    single_invoice_upload,
)
from backend.schemas.ksef import KsefInvoiceUploadStatus
from backend.db.repositories.ksef_credentials_repository import get_auth_certs

from backend.settings import Settings


async def get_pretty_invoice_xml(db_session: AsyncSession, invoice_id: str) -> str:
    """Pull invoice XML from DB and prettify it."""
    xml = await get_invoice_xml(db_session, invoice_id)

    parser = FA3XmlParser()
    builder = FA3XmlBuilder()

    fa3 = parser.parse_string(xml)

    return builder.build_pretty_xml(fa3)