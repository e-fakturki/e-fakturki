import axios from "axios";
import { apiConfig } from "../../config";
import type {
  ProductCreationRequest,
  ProductCreateResponse,
  TaxRate,
  GetProductsListRequest,
  GetProductsListResponse,
} from "../types/products";

const baseUrl = apiConfig.apiBaseUrl + apiConfig.endpoints.products;

export const createProduct = async (
  data: ProductCreationRequest,
): Promise<ProductCreateResponse> => {
  try {
    const response = await axios.post<ProductCreateResponse>(baseUrl, data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateProduct = async (
  data: ProductCreationRequest,
): Promise<ProductCreateResponse> => {
  try {
    const response = await axios.put<ProductCreateResponse>(baseUrl, data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getProductsList = async (
  data: GetProductsListRequest,
): Promise<GetProductsListResponse> => {
  try {
    const response = await axios.get<GetProductsListResponse>(
      `${baseUrl}?company_id=${data.company_id}&search_string=${data.search_string ? data.search_string : ""}&page_size=${data.page_size}&page_offset=${data.page_offset}`,
    );

    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteProduct = async (product_id: string): Promise<string> => {
  try {
    const response = await axios.delete<string>(`${baseUrl}/${product_id}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getTaxRates = async (): Promise<TaxRate[]> => {
  try {
    const response = await axios.get<TaxRate[]>(`${baseUrl}/tax-rates`);
    return response.data;
  } catch (error) {
    throw error;
  }
};
