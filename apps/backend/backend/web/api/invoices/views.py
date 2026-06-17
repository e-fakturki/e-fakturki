from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Literal

from backend.db.repositories.invoice_xml_repository import insert_invoice_xml
from backend.domain.fa3_xml_utils.utils.builder import FA3XmlBuilder
from backend.domain.fa3_xml_utils.utils.validator import Fa3XmlValidator
from backend.domain.fa3_xml_utils.utils.mapper import FA3ObjectMapper
from backend.db.repositories.invoices_payment_repository import insert_invoice_payment_details_from_invoice_object
from backend.db.repositories.invoices_entries_repository import insert_invoice_entries_from_invoice_object
from backend.db.repositories.invoices_details_repository import insert_invoice_details_from_invoice_object
from backend.db.dependencies import get_db_session
from backend.db.repositories.company_repository import get_company_nip
from backend.db.models.invoices_payment import PaymentStatus
from backend.web.api.invoices.services import get_pretty_invoice_xml
from backend.schemas.auth import UserRead
from backend.web.api.auth.services import get_current_user
from backend.schemas.ksef import SalesInvoicesRequest
from backend.schemas.invoices import InvoiceObjectRequest, InvoiceResponse, InvoicesListResponse
from backend.db.repositories.invoices_brief_repository import (
    get_company_invoices_list,
    insert_invoice_brief_form_invoice_object,
    update_invoice_payment_status,
    update_invoice_is_new_status,
)

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/list", status_code=200, response_model=InvoicesListResponse)
async def get_invoices_list(
    payload: SalesInvoicesRequest,
    invoice_type: Literal["sales", "purchases"],
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> InvoicesListResponse:
    """Download the invoices metadata list from DB."""
    company_nip = await get_company_nip(db_session, payload.company_id)

    return await get_company_invoices_list(
        db=db_session,
        filters=payload,
        company_nip=company_nip,
        invoice_type=invoice_type,
    )


@router.get("/{invoice_id}/pretty-xml", status_code=200, response_model=str)
async def get_invoice_xml(
    invoice_id: str = Path(..., description="The ID of the invoice."),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> str:
    """Get the formatted invoice XML from the database."""
    try:
        return await get_pretty_invoice_xml(db_session, invoice_id)
    except (IntegrityError, SQLAlchemyError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch("/{invoice_id}/payment-status", status_code=204)
async def update_payment_status(
    invoice_id: str = Path(..., description="The ID of the invoice to update."),
    new_payment_status: PaymentStatus = Query(
        ..., description="The new payment status to set for the invoice."
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> None:
    """Update the payment status of an invoice in the database."""

    try:
        success = await update_invoice_payment_status(
            db_session, invoice_id, new_payment_status
        )
        if not success:
            raise HTTPException(status_code=404, detail="Invoice not found")
    except (IntegrityError, SQLAlchemyError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch("/{invoice_id}/is-new", status_code=204)
async def update_new_status(
    invoice_id: str = Path(..., description="The ID of the invoice to update."),
    is_new: bool = Body(
        ..., description="Whether the invoice is new or not.", embed=True
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> None:
    """Update the is_new status of an invoice in the database."""

    try:
        success = await update_invoice_is_new_status(db_session, invoice_id, is_new)
        if not success:
            raise HTTPException(status_code=404, detail="Invoice not found")
    except (IntegrityError, SQLAlchemyError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{company_id}", status_code=200, response_model=str)
async def post_invoice(
    payload: InvoiceObjectRequest,
    company_id: str = Path(..., description="The ID of the company."),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> str:
    """Upload the invoice and save to DB."""

    # verify the entries sums match with the invoice totals

    try:
        brief_id = await insert_invoice_brief_form_invoice_object(db_session, payload)
        await insert_invoice_details_from_invoice_object(db_session, payload, brief_id)
        await insert_invoice_entries_from_invoice_object(db_session, payload, brief_id)
        await insert_invoice_payment_details_from_invoice_object(db_session, payload, brief_id)

        fa3_mapper = FA3ObjectMapper()
        fa3_xml_builder = FA3XmlBuilder()
        fa3_xml_validator = Fa3XmlValidator()

        fa3_object = fa3_mapper.build_fa3_invoice_from_invoice_object(payload)

        xml = fa3_xml_builder.build_plain_xml(fa3_object)

        if(fa3_xml_validator.validate(xml)):
            await insert_invoice_xml(db_session, brief_id, xml, sha256_base64=None)
        else:
            raise HTTPException(status_code=422, detail="Invalid XML")

    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail=e.args[0],
        ) from e

    return brief_id

