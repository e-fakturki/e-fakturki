import type { PageInfo } from "./common";
export interface KsefCredentials {
  certFile: File | null;
  keyFile: File | null;
  certPassword: string;
}

export interface KsefCredentialsCreationRequest {
  company_id: string;
  online_certificates: boolean;
  certificate: File;
  private_key: File;
  password: string;
}

export interface KsefCredentialsCreationResponse {
  company_id: string;
  credentials_id: number;
}

const invoiceTypes = ["purchase", "sales"] as const;
export type InvoiceType = (typeof invoiceTypes)[number];
export interface getInvoicesListRequest {
  company_id: string;
  date_from: string;
  date_to: string;
  page_size: number;
  page_offset: number;
}

export interface invoiceListItem {
  id: string;
  invoice_number: string;
  issued_date: string;
  is_new: boolean;
  seller_name: string;
  buyer_name: string;
  gross_total: number;
  currency: string;
  payment_type: string | null;
  payment_status: string | null;
  ksef_number: string | null;
  ksef_status: string;
}

export interface getInvoicesListResponse {
  invoices: invoiceListItem[];
  page_info: PageInfo;
}

export interface postInvoiceToKsefResponse {
  ksef_number: string;
  invoicing_date: string;
  acquisition_date: string;
  permanent_storage_date: string;
}
