from fastapi import APIRouter, Depends, Query, Path
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from backend.db.dependencies import get_db_session
from backend.db.models.products import (
    tax_rates_descriptions,
    tax_rate_values,
    tax_rates_display,
)
from backend.schemas.products import (
    ProductCreate,
    ProductCreateResponse,
    ProductListResponse,
    ProductUpdate,
    TaxRate,
)
from backend.db.repositories.product_repository import (
    get_products_list_paginated,
    insert_new_product,
    delete_product_record,
    update_product_data
)
from backend.web.api.products.services import check_and_set_gross_price
from backend.schemas.auth import UserRead
from backend.web.api.auth.services import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", status_code=201, response_model=ProductCreateResponse)
async def create_product(
    payload: ProductCreate,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> ProductCreateResponse:
    """Create a new product record."""
    # payload = check_and_set_gross_price(payload)
    try:
        return await insert_new_product(db_session, payload)
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail=e.args[0],
        ) from e


@router.put("", status_code=201, response_model=ProductCreateResponse)
async def update_product(
    payload: ProductUpdate,
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> ProductCreateResponse:
    """Update a product record."""
    try:
        product_update_response = await update_product_data(db_session, payload)
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail=e.args[0],
        ) from e

    return product_update_response


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: str = Path(
        ..., description="The ID of the product to delete from the db."
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a product record."""
    try:
        await delete_product_record(db_session, product_id)
    except NoResultFound as e:
        raise HTTPException(
            status_code=422,
            detail="W bazie danych nie ma produktu z podanym ID",
        ) from e


@router.get("", status_code=200, response_model=ProductListResponse)
async def get_products_list(
    company_id: str = Query(..., description="The ID of the company to filter by."),
    search_string: str = Query(
        None, description="The search string to filter the product list."
    ),
    page_size: int = Query(
        10,
        description="The number of product records to retrieve per page. [10 ... 250]",
    ),
    page_offset: int = Query(
        0,
        description="The offset for pagination, i.e. the number of records to skip before starting to collect the result set.",
    ),
    current_user: UserRead = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> ProductListResponse:
    """Get all company records."""

    try:
        return await get_products_list_paginated(
            db=db_session,
            company_id=company_id,
            search_string=search_string,
            page_size=page_size,
            page_offset=page_offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/tax-rates", response_model=list[TaxRate])
async def get_tax_rates(
    db_session: AsyncSession = Depends(get_db_session),
) -> list[TaxRate]:
    """Get all tax rates."""

    tax_rates: list[TaxRate] = [
        TaxRate(
            display_text=tax_rates_display[text],
            str_repr=text,
            hint_text=description,
            value=tax_rate_values[text],
        )
        for text, description in tax_rates_descriptions.items()
    ]

    return tax_rates
