export interface PageInfo {
  current_page: number;
  page_size: number;
  total_items: number;
  has_next_page: boolean;
  has_previous_page: boolean;
}

export interface PaginationRequest {
  search_string: string | null;
  page_size: number;
  page_offset: number;
}
