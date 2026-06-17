import type { PageInfo } from "./common";

export interface IsoCountries {
  label: string;
  value: string;
}

export interface CompanyBase {
  owner_id: string | null;
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
  additional_info: string | null;
}

export interface CompanyCreate extends CompanyBase {}

export interface CompanyCreateResponse {
  id: string;
  owner_id: string | null;
}

export interface CompanyReadUpdate extends CompanyBase {
  id: string;
}

export interface UserCompanyResponse extends CompanyBase {
  id: string;
  ksef_authorized: boolean;
}

export interface CompaniesListResponse {
  companies: CompanyReadUpdate[];
  page_info: PageInfo;
}

export type CreateOrUpdate = "create" | "update";
