from fastapi import APIRouter, Depends, Form, Path, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.db.repositories.invoice_xml_repository import get_invoice_xml
from backend.domain.fa3_xml_utils.utils.builder import FA3XmlBuilder
from backend.domain.fa3_xml_utils.utils.mapper import FA3ObjectMapper
from backend.domain.fa3_xml_utils.utils.validator import Fa3XmlValidator
from backend.services.ksef.invoicing.upload import post_invoice_to_ksef
from backend.schemas.invoices import InvoiceObjectRequest
from backend.db.dependencies import get_db_session
from backend.schemas.auth import UserRead
from backend.web.api.auth.services import get_current_user
from backend.schemas.ksef import KsefInvoiceUploadStatus

router = APIRouter()


@router.post("/{company_id}/single_upload", status_code=202, response_model=KsefInvoiceUploadStatus)
async def upload_invoice_to_ksef(
    payload: InvoiceObjectRequest,
    company_id: str = Path(
        ..., description="The ID of the company issuing the invoice."
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> KsefInvoiceUploadStatus:
    """Upload single invoice to ksef."""
    fa3_mapper = FA3ObjectMapper()
    fa3_xml_builder = FA3XmlBuilder()
    fa3_xml_validator = Fa3XmlValidator()

    fa3_object = fa3_mapper.build_fa3_invoice_from_invoice_object(payload)

    xml = fa3_xml_builder.build_plain_xml(fa3_object)

    if(fa3_xml_validator.validate(xml)):
        xml_bytes = fa3_xml_builder.build_bytes_xml(fa3_object)
        return await post_invoice_to_ksef(db_session, company_id, xml_bytes)
    return None


@router.post("/{company_id}/single_xml_upload/{invoice_id}", status_code=202, response_model=KsefInvoiceUploadStatus)
async def upload_invoice_xml_to_ksef(
    company_id: str = Path(
        ..., description="The ID of the company issuing the invoice."
    ),
    invoice_id: str = Path(
        ..., description="The ID of the invoice."
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> KsefInvoiceUploadStatus:
    """Upload single invoice to ksef."""

    try:
        fa3_xml_validator = Fa3XmlValidator()

        xml = await get_invoice_xml(db_session, invoice_id)

        if(fa3_xml_validator.validate(xml)):
            xml_bytes = xml.encode("utf-8")
            return await post_invoice_to_ksef(db_session, company_id, xml_bytes)
        return None
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail=e.args[0],
        ) from e
