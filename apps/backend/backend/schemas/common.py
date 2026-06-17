from pydantic import BaseModel, Field


class PageInfo(BaseModel):
    """Pagination information for invoice list responses."""

    current_page: int = Field(1, description="The current page number. [1 ... n]")
    page_size: int = Field(
        10,
        description="The number of invoice records to retrieve per page. [10 ... 250]",
    )
    total_items: int = Field(0, description="The total number of invoice records.")
    has_next_page: bool = Field(
        False, description="Indicates whether the next page exists."
    )
    has_previous_page: bool = Field(
        False, description="Indicates whether the previous page exists."
    )


class PaginationRequest(BaseModel):
    """Pagination information for paginted lists requests."""

    search_string: str = Field(
        None, description="The search string to filter the company list."
    )
    page_size: int = Field(
        10,
        description="The number of company records to retrieve per page. [10 ... 250]",
    )
    page_offset: int = Field(
        0,
        description="The offset for pagination, i.e. the number of records to skip before starting to collect the result set.",
    )
