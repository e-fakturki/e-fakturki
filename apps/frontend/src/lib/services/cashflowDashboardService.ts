import axios from "axios";
import { apiConfig } from "../../config";
import type { CashflowListItem, MonthlyProfitItem, MonthlySalesSummary } from "../types/cashflow";
import type { invoiceTableType } from "../types/invoices";

const baseUrl = apiConfig.apiBaseUrl + apiConfig.endpoints.cashflow;

export const getMonthlyProfitList = async (
  companyId: string,
  year: number,
): Promise<MonthlyProfitItem[]> => {
  try {
    const response = await axios.get<MonthlyProfitItem[]>(
      `${baseUrl}/monthly-profits?company_id=${companyId}&year=${year}`,
    );

    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getMonthlySalesSummary = async (
  companyId: string,
  year: number,
  month: number | null,
): Promise<MonthlySalesSummary> => {
  try {
    const response = await axios.get<MonthlySalesSummary>(
      `${baseUrl}/monthly-sales-summary?company_id=${companyId}&year=${year}&month=${month}`,
    );

    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getCashflowListLazy = async (
  companyId: string,
  year: number,
  month: number | null,
  type: invoiceTableType,
  offset: number = 0,
  limit: number = 50,
  sortBy?: string | null,
  sortOrder?: "asc" | "desc" | null,
): Promise<CashflowListItem[]> => {
  try {
    const response = await axios.get<CashflowListItem[]>(
      `${baseUrl}/month-cashflow-list?company_id=${companyId}&year=${year}&month=${month}&type=${type}&offset=${offset}&limit=${limit}${sortBy ? `&sort_by=${sortBy}` : ""}${sortOrder ? `&sort_order=${sortOrder}` : ""}`,
    );

    return response.data;
  } catch (error) {
    throw error;
  }
};
