from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, update

from backend.domain.fa3_xml_utils.models.schemat import TstawkaPodatku
from backend.schemas.invoices import PageInfo
from backend.db.models.products import ProductsTable
from backend.schemas.products import (
    ProductListItem,
    ProductListResponse,
    ProductCreate,
    ProductCreateResponse,
    ProductUpdate,
)


async def insert_new_product(
    db: AsyncSession, payload: ProductCreate
) -> ProductCreateResponse | None:
    """Insert a new product into the database."""
    try:
        product = ProductsTable(
            company_id=payload.company_id,
            name=payload.name,
            description=payload.description,
            gtin=payload.gtin,
            unit=payload.unit,
            net_price=payload.net_price,
            tax_rate=TstawkaPodatku(payload.tax_rate),
            gross_price=payload.gross_price,
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)

        return ProductCreateResponse(id=product.id, company_id=product.company_id)

    except IntegrityError:
        await db.rollback()
        raise


async def update_product_data(
    db: AsyncSession, payload: ProductUpdate
) -> ProductCreateResponse | None:
    """Update a product record in the database."""
    try:
        await db.execute(
            update(ProductsTable)
            .where(ProductsTable.id == payload.id)
            .values(
                name=payload.name,
                description=payload.description,
                gtin=payload.gtin,
                unit=payload.unit,
                net_price=payload.net_price,
                tax_rate=TstawkaPodatku(payload.tax_rate),
                gross_price=payload.gross_price,
            )
        )

        await db.commit()
        return ProductCreateResponse(id=payload.id, company_id=payload.company_id)

    except IntegrityError:
        await db.rollback()
        raise


async def delete_product_record(db: AsyncSession, product_id: str) -> str:
    """Delete a product record from the database."""
    stmt = select(ProductsTable).where(ProductsTable.id == product_id).limit(1)
    result = await db.execute(stmt)
    product = result.scalar_one()
    await db.delete(product)
    await db.commit()
    return product_id


async def get_products_list_paginated(
    db: AsyncSession,
    company_id: str,
    search_string: str | None,
    page_size: int,
    page_offset: int,
) -> list[ProductListResponse]:
    """Get a paginated list of product records."""

    # Get total count of products
    total_items = await db.execute(select(func.count(ProductsTable.id)))
    total_items = total_items.scalar()

    # get the products
    products = await db.execute(
        select(
            ProductsTable.id,
            ProductsTable.name,
            ProductsTable.description,
            ProductsTable.gtin,
            ProductsTable.unit,
            ProductsTable.net_price,
            ProductsTable.tax_rate,
            ProductsTable.gross_price,
        )
        .where(
            or_(
                ProductsTable.name.contains(search_string),
                ProductsTable.description.contains(search_string),
                ProductsTable.gtin.contains(search_string),
            )
        )
        .where(ProductsTable.company_id == company_id)
        .offset(page_offset)
        .limit(page_size)
        .order_by(ProductsTable.name)
    )
    products = [ProductListItem(**product) for product in products.mappings().all()]

    # prepare page info
    page_info = PageInfo(
        current_page=(page_offset // page_size) + 1 if total_items > 0 else 1,
        page_size=page_size,
        total_items=total_items,
        has_next_page=(page_offset + page_size) < total_items,
        has_previous_page=page_offset > 0,
    )

    return ProductListResponse(products=products, page_info=page_info)
