import axios from "axios";
import type { getInvoicesListRequest, getInvoicesListResponse, InvoiceType } from "../types/ksef";
import { apiConfig } from "../../config";
import type { InvoiceObject } from "../types/invoices";

const baseUrl = apiConfig.apiBaseUrl + apiConfig.endpoints.invoices;

export const getInvoicesList = async (
  data: getInvoicesListRequest,
  invoiceType: InvoiceType,
): Promise<getInvoicesListResponse> => {
  try {
    const response = await axios.post<getInvoicesListResponse>(`${baseUrl}/list`, data, {
      params: {
        invoice_type: invoiceType,
      },
    });

    return response.data;
  } catch (error) {
    console.log(error.response?.data?.detail);
    throw error;
  }
};

export const updateInvoiceIsNew = async (invoice_id: string, is_new: boolean): Promise<number> => {
  try {
    const response = await axios.patch(`${baseUrl}/${invoice_id}/is-new`, {
      is_new: is_new,
    });
    return response.status;
  } catch (error) {
    console.log(error.response?.data?.detail);
    throw error;
  }
};

export const saveCreatedInvoice = async (
  data: InvoiceObject,
  companyId: string,
): Promise<string> => {
  try {
    const response = await axios.post<string>(`${baseUrl}/${companyId}`, data);

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const responseData = error.response?.data as { detail?: string } | undefined;
      if (responseData?.detail) {
        switch (true) {
          case responseData.detail.includes("invoices_brief.invoice_number"):
            responseData.detail = "Faktura z tym numerem już istnieje w bazie danych.";
            break;
          default:
            break;
        }
      }
    }
    throw error;
  }
};
