from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from backend.schemas.common import PaginationRequest
from backend.db.dependencies import get_db_session
from backend.db.repositories.company_repository import (
    get_company_by_user_id,
    insert_new_company,
    delete_company_record,
    update_company_data,
    get_companies_list_paginated,
)
from backend.domain.fa3_xml_utils.models.kody_krajow_v10_0_e import TkodKraju
from backend.web.api.companies.services import get_polish_country_name
from backend.db.repositories.ksef_credentials_repository import get_ksef_credentials
from backend.schemas.auth import UserRead
from backend.web.api.auth.services import get_current_user
from backend.schemas.companies import (
    CompanyCreate,
    CompanyCreateResponse,
    CompanyReadUpdate,
    IsoCountry,
    UserCompanyResponse,
    CompaniesListResponse,
)

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", status_code=201, response_model=CompanyCreateResponse)
async def create_company(
    payload: CompanyCreate,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> CompanyCreateResponse:
    """Create a new company record."""
    try:
        company_response = await insert_new_company(db_session, payload)
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail=e.args[0],
        ) from e

    return company_response


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: str = Path(
        ..., description="The ID of the company to delete from the db."
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a company record."""
    try:
        await delete_company_record(db_session, company_id)
    except NoResultFound as e:
        raise HTTPException(
            status_code=409,
            detail="W bazie danych nie ma firmy z podanym ID",
        ) from e


@router.put("", status_code=201, response_model=CompanyCreateResponse)
async def update_company(
    payload: CompanyReadUpdate,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> CompanyCreateResponse:
    """Update a company record."""
    try:
        company_update_response = await update_company_data(db_session, payload)
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail=e.args[0],
        ) from e

    return company_update_response


@router.get("/me", status_code=200, response_model=UserCompanyResponse)
async def get_user_company(
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> UserCompanyResponse:
    """Fetch the company information associated with the current user."""

    company = await get_company_by_user_id(db_session, current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found for the user.")

    # check if company has KSeF credentials in the DB
    ksef_creds = await get_ksef_credentials(db_session, company.id)
    if not (
        ksef_creds.cert_auth
        and ksef_creds.private_key_auth
        and ksef_creds.password_auth
    ):
        raise HTTPException(
            status_code=409, detail="KSeF credentials not found for the company."
        )

    return UserCompanyResponse(
        id=company.id,
        owner_id=company.owner_id,
        name=company.name,
        nip=company.nip,
        krs=company.krs,
        regon=company.regon,
        country_code=company.country_code,
        address_l1=company.address_l1,
        address_l2=company.address_l2,
        address_correspondance_l1=company.address_correspondance_l1,
        address_correspondance_l2=company.address_correspondance_l2,
        email=company.email,
        phone_number=company.phone_number,
        additional_info=company.additional_info,
        ksef_authorized=True,
    )


@router.get("/list", status_code=200, response_model=CompaniesListResponse)
async def get_companies_list(
    pagination: PaginationRequest = Depends(),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> CompaniesListResponse:
    """Get all company records."""

    try:
        return await get_companies_list_paginated(db_session, pagination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/iso-countries", status_code=200, response_model=list[IsoCountry])
async def get_iso_countries(
    current_user: UserRead = Depends(get_current_user),
) -> list[IsoCountry]:
    """Get all ISO countries list."""

    return [get_polish_country_name(iso_country.value) for iso_country in TkodKraju]
