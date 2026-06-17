export const ksefStatusSeverity = {
  not_sent: "warn",
  sent: "info",
  rejected: "danger",
  accepted: "success",
};

export const ksefStatusIcon = {
  not_sent: "pi pi-hourglass",
  sent: "pi pi-send",
  rejected: "pi pi-times",
  accepted: "pi pi-check-circle",
};

export const ksefStatusHint = {
  not_sent: "Nie wysłano do KSeF",
  sent: "W trakcie wysyłania do KSeF",
  rejected: "Faktura odrzucona przez KSeF",
  accepted: "Faktura obecna w systemie KSeF",
};

export const paymentType = {
  1: "Gotówka",
  2: "Karta",
  3: "Bon",
  4: "Czek",
  5: "Kredyt/Pożyczka",
  6: "Przelew",
  7: "Płatność mobilna",
};

export const paymentTypeMapForComponents = [
  { label: "Gotówka", value: 1 },
  { label: "Karta", value: 2 },
  { label: "Bon", value: 3 },
  { label: "Czek", value: 4 },
  { label: "Kredyt/Pożyczka", value: 5 },
  { label: "Przelew", value: 6 },
  { label: "Płatność mobilna", value: 7 },
];

export const paymentStatus = {
  paid: "Opłacono",
  partial: "Częściowo opłacono",
  unpaid: "Nie opłacono",
};

export const paymentStatusMapForComponents = [
  { label: "Nie opłacono", value: "unpaid" },
  { label: "Opłacono", value: "paid" },
  { label: "Częściowo opłacono", value: "partial" },
];

export const paymentStatusSeverity = {
  paid: "success",
  partial: "warn",
  unpaid: "danger",
};

export type invoiceTableType = "sales" | "purchases";

export interface InvoiceEntry {
  row_number: number;
  delivery_date: string | null;
  name: string;
  amount: number;
  unit: string;
  net_price: number;
  gross_price: number | null;
  net_total: number;
  tax_rate: string;
  tax_total: number | null;
  gross_total: number;
}

export interface InvoiceCompanyData {
  name: string;
  nip: string;
  krs: string | null;
  regon: string | null;
  country_code: string;
  address_l1: string | null;
  address_l2: string | null;
  address_correspondance_l1: string | null;
  address_correspondance_l2: string | null;
  email: string | null;
  phone_number: string | null;
}

export interface InvoicePayment {
  payment_status: string;
  payment_type: string;
  payment_date: string | null;
  payment_due_date: string | null;
  partial_payments: string | null;
  seller_bank_account_number: string | null;
  seller_bank_name: string | null;
}

export interface InvoiceObject {
  id: string | null;
  invoice_number: string;
  invoice_type: string;
  ksef_number: string | null;
  invoicing_date: string | null;
  acquisition_date: string | null;
  permanent_storage_date: string | null;
  ksef_status: string;
  is_new: boolean;
  issue_date: string;
  issue_place: string;
  seller_info: InvoiceCompanyData;
  buyer_info: InvoiceCompanyData;
  entries: InvoiceEntry[];
  currency: string;
  net_total: number;
  tax_total: number;
  gross_total: number;
  payment: InvoicePayment;
  annotations: string | null;
  additional_info: string | null;
  footer_info: string | null;
  footer_registers: string | null;
}
