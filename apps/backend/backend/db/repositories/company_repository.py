from sqlalchemy import select, func, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.db.models.companies import CompaniesTable
from backend.schemas.companies import (
    CompaniesListResponse,
    CompanyCreate,
    CompanyCreateResponse,
    CompanyReadUpdate,
)
from backend.schemas.common import PageInfo, PaginationRequest


async def get_company_nip(db: AsyncSession, company_id: int) -> str:
    """Get company NIP based on company ID."""
    stmt = select(CompaniesTable.nip).where(CompaniesTable.id == company_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def delete_company_record(db: AsyncSession, company_id: str) -> bool:
    """Delete a company record from the database."""
    stmt = select(CompaniesTable).where(CompaniesTable.id == company_id).limit(1)
    result = await db.execute(stmt)
    company = result.scalar_one()
    await db.delete(company)
    await db.commit()
    return True


async def get_company_by_user_id(
    db: AsyncSession, user_id: str
) -> CompaniesTable | None:
    """Get the company information associated with a given user ID."""
    stmt = select(CompaniesTable).where(CompaniesTable.owner_id == user_id).limit(1)
    result = await db.execute(stmt)
    return result.scalar_one()


async def insert_new_company(
    db: AsyncSession, payload: CompanyCreate
) -> CompanyCreateResponse | None:
    """Insert a new company into the database."""
    try:
        company = CompaniesTable(**payload.model_dump())
        db.add(company)
        await db.commit()
        await db.refresh(company)

        return CompanyCreateResponse(owner_id=company.owner_id, id=company.id)

    except IntegrityError:
        await db.rollback()
        raise


async def update_company_data(
    db: AsyncSession, payload: CompanyReadUpdate
) -> CompanyCreateResponse | None:
    """Update a company record in the database."""
    try:
        await db.execute(
            update(CompaniesTable)
            .where(CompaniesTable.id == payload.id)
            .values(
                name=payload.name,
                nip=payload.nip,
                krs=payload.krs,
                regon=payload.regon,
                email=payload.email,
                phone_number=payload.phone_number,
                country_code=payload.country_code,
                address_l1=payload.address_l1,
                address_l2=payload.address_l2,
                address_correspondance_l1=payload.address_correspondance_l1,
                address_correspondance_l2=payload.address_correspondance_l2,
                additional_info=payload.additional_info,
            )
        )

        await db.commit()
        return CompanyCreateResponse(owner_id=payload.owner_id, id=payload.id)

    except IntegrityError:
        await db.rollback()
        raise


async def get_companies_list_paginated(
    db: AsyncSession, pagination: PaginationRequest
) -> list[CompaniesListResponse]:
    """Get a paginated list of company records."""

    # Get total count of companies
    total_items = await db.execute(select(func.count(CompaniesTable.id)))
    total_items = total_items.scalar()

    query = select(CompaniesTable)
    if pagination.search_string:
        query = query.where(
            or_(
                CompaniesTable.name.contains(pagination.search_string),
                CompaniesTable.nip.contains(pagination.search_string),
                CompaniesTable.address_l1.contains(pagination.search_string),
                CompaniesTable.address_l2.contains(pagination.search_string),
                CompaniesTable.email.contains(pagination.search_string),
                CompaniesTable.phone_number.contains(pagination.search_string),
            )
        )
    query = (
        query.offset(pagination.page_offset)
        .limit(pagination.page_size)
        .order_by(CompaniesTable.name)
    )
    result = await db.execute(query)
    companies = [
        CompanyReadUpdate.model_validate(company) for company in result.scalars().all()
    ]

    # prepare page info
    page_info = PageInfo(
        current_page=(pagination.page_offset // pagination.page_size) + 1
        if total_items > 0
        else 1,
        page_size=pagination.page_size,
        total_items=total_items,
        has_next_page=(pagination.page_offset + pagination.page_size) < total_items,
        has_previous_page=pagination.page_offset > 0,
    )

    return CompaniesListResponse(companies=companies, page_info=page_info)
