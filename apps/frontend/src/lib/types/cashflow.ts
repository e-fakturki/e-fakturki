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

export interface MonthlyProfitItem {
  month_number: number;
  net_sales: number;
  net_costs: number;
  net_profit: number;
}

export interface MonthlySalesSummary {
  year_number: number;
  month_number: number;
  sales_amount: number;
  avg_sale_value: number;
  costs_amount: number;
  avg_cost_value: number;
  new_customers: number;
  inactive_customers: number;
  unpaid_sales: number;
  unpaid_costs: number;
}

export interface CashflowListItem {
  year_number: number;
  month_number: number;
  id: string;
  issue_date: string;
  type: string;
  contractor_name: string;
  net_value: number;
  payment_status: string;
}
