import axios from "axios";
import { apiConfig } from "../../config";
import type { MonthlyProfitItem, MonthlySalesSummary } from "../types/cashflow";

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
