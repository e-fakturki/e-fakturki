import type { pageInfo } from "../types/ksef";

export interface GetProductsListRequest {
  company_id: string;
  search_string: string | null;
  page_size: number;
  page_offset: number;
}

export interface ProductListItem {
  id: string;
  name: string;
  description: string | null;
  gtin: string | null;
  unit: string | null;
  net_price: number | null;
  tax_rate: string | null;
  gross_price: number | null;
}

export interface GetProductsListResponse {
  products: ProductListItem[];
  page_info: pageInfo;
}

export interface TaxRate {
  display_text: string;
  hint_text: string;
  str_repr: string;
  value: number;
}

export interface ProductCreationRequest {
  id: string;
  company_id: string;
  name: string;
  description: string | null;
  gtin: string | null;
  unit: string | null;
  net_price: number | null;
  tax_rate: string | null;
  gross_price: number | null;
}

export interface ProductCreateResponse {
  id: string;
  company_id: string;
}
