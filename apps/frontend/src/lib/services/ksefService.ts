import axios from "axios";
import type {
  InvoiceType,
  KsefCredentialsCreationRequest,
  KsefCredentialsCreationResponse,
  getInvoicesListRequest,
  postInvoiceToKsefResponse,
} from "../types/ksef";
import { apiConfig } from "../../config";
import type { InvoiceObject } from "../types/invoices";

const baseUrl = apiConfig.apiBaseUrl + apiConfig.endpoints.ksef;

export const createKsefCredentials = async (
  data: KsefCredentialsCreationRequest,
): Promise<KsefCredentialsCreationResponse> => {
  try {
    const formData = new FormData();

    formData.append("company_id", String(data.company_id));
    formData.append("online_certificates", String(data.online_certificates));
    formData.append("certificate", data.certificate);
    formData.append("private_key", data.private_key);
    formData.append("password", data.password);

    const response = await axios.post<KsefCredentialsCreationResponse>(
      baseUrl + "/certificates",
      formData,
    );

    return response.data;
  } catch (error) {
    throw error;
  }
};

export const refreshInvoiceListFromKsef = async (
  data: getInvoicesListRequest,
  invoiceType: InvoiceType,
): Promise<string[]> => {
  console.log(data);
  try {
    const response = await axios.post<string[]>(baseUrl + "/invoices", data, {
      params: {
        invoice_type: invoiceType,
      },
    });

    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getInvoiceDetails = async (
  company_id: number,
  invoice_id: string,
): Promise<InvoiceObject> => {
  try {
    const response = await axios.post<InvoiceObject>(
      `${baseUrl}/single_invoice_download/${company_id}/${invoice_id}`,
    );
    console.log(response.data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const postInvoiceToKsef = async (
  data: InvoiceObject,
  companyId: string,
): Promise<postInvoiceToKsefResponse> => {
  try {
    const response = await axios.post<postInvoiceToKsefResponse>(
      `${baseUrl}/${companyId}/single_upload`,
      data,
    );
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const postInvoiceXmlToKsef = async (
  companyId: string,
  invoiceId: string,
): Promise<postInvoiceToKsefResponse> => {
  try {
    const response = await axios.post<postInvoiceToKsefResponse>(
      `${baseUrl}/${companyId}/single_xml_upload/${invoiceId}`,
    );
    return response.data;
  } catch (error) {
    throw error;
  }
};
