import type { TaxRate } from "./products";

export interface IncomeType {
  value: string;
  label: string;
  description: string;
}

export interface PaymentStatusType {
  value: string;
  label: string;
}

export interface NewCashflowRecord {
  id: string;
  type: string;
  date: string;
  name: string;
  description: string | null;
  netValue: number;
  taxRate: string;
  paymentStatus: string;
}
