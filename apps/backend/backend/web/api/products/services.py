from math import isclose
from decimal import ROUND_HALF_UP, Decimal

from backend.schemas.products import ProductCreate, ProductUpdate
from backend.db.models.products import tax_rate_values
from backend.services.invoices.entries_validator import MONEY_TOLERANCE


def check_and_set_gross_price(payload: ProductCreate | ProductUpdate) -> ProductCreate | ProductUpdate:
    """
    Validate the gross price, and fix if needed.

    Args:
        payload: The data for creating/updating a product record.

    Returns:
        Payload object.
    """
    if payload.net_price and payload.tax_rate:
        tax_rate_value = 1 + tax_rate_values[payload.tax_rate]
        expected_gross_price = round(payload.net_price * tax_rate_value, 2)

        if not isclose(payload.gross_price, expected_gross_price, abs_tol=MONEY_TOLERANCE):
            payload.gross_price = expected_gross_price

    # if not payload.gross_price or payload.gross_price == 0:
    #     net_price = Decimal(payload.net_price)
    #     tax_rate = Decimal(payload.tax_rate)

    #     payload.gross_price = (
    #         net_price * (Decimal("1") + tax_rate / Decimal("100"))
    #     ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # return payload
