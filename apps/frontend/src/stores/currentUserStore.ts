import { defineStore } from "pinia";
import type { UserCompanyResponse } from "../lib/types/company";

export const useCurrentUserStore = defineStore("currentUser", {
  state: () => {
    return {
      userId: "" as string,
      name: null as string | null,
      lastname: null as string | null,
      email: null as string | null,
      token: null as string | null,

      selectedCompany: null as UserCompanyResponse | null,
    };
  },
  getters: {
    getUserId: (state) => state.userId,
    getName: (state) => state.name,
    getLastname: (state) => state.lastname,
    getFullName: (state) => {
      if (state.name && state.lastname) {
        return `${state.name} ${state.lastname}`;
      }
      return null;
    },
    getToken: (state) => state.token,
    getEmail: (state) => state.email,
    getCompanyId: (state) => state.selectedCompany?.id,
    getCompanyName: (state) => state.selectedCompany?.name,
    getCompanyNip: (state) => state.selectedCompany?.nip,
    getCompanyKrs: (state) => state.selectedCompany?.krs,
    getCompanyRegon: (state) => state.selectedCompany?.regon,
    getCompanyCountryCode: (state) => state.selectedCompany?.country_code,
    getCompanyAddressL1: (state) => state.selectedCompany?.address_l1,
    getCompanyAddressL2: (state) => state.selectedCompany?.address_l2,
    getCompanyAddressCorrespondanceL1: (state) => state.selectedCompany?.address_correspondance_l1,
    getCompanyAddressCorrespondanceL2: (state) => state.selectedCompany?.address_correspondance_l2,
    getCompanyEmail: (state) => state.selectedCompany?.email,
    getCompanyPhoneNumber: (state) => state.selectedCompany?.phone_number,
    getCompanyAdditionalInfo: (state) => state.selectedCompany?.additional_info,

    getUserCompanyReadUpdate: (state) => {
      return {
        id: state.selectedCompany?.id,
        owner_id: state.selectedCompany?.owner_id,
        name: state.selectedCompany?.name,
        nip: state.selectedCompany?.nip,
        krs: state.selectedCompany?.krs,
        regon: state.selectedCompany?.regon,
        country_code: state.selectedCompany?.country_code,
        address_l1: state.selectedCompany?.address_l1,
        address_l2: state.selectedCompany?.address_l2,
        address_correspondance_l1: state.selectedCompany?.address_correspondance_l1,
        address_correspondance_l2: state.selectedCompany?.address_correspondance_l2,
        email: state.selectedCompany?.email,
        phone_number: state.selectedCompany?.phone_number,
        additional_info: state.selectedCompany?.additional_info,
      };
    },

    isCompanyKsefAuthorized: (state) => state.selectedCompany?.ksef_authorized,
  },
  actions: {
    setToken(token: string) {
      this.token = token;
    },
    setUserData(userId: string, name: string, lastname: string, email: string, token: string) {
      this.userId = userId;
      this.name = name;
      this.lastname = lastname;
      this.email = email;
      this.token = token;
    },
    setCompanyData(company_data: UserCompanyResponse) {
      this.selectedCompany = company_data;
    },
    setCompanyKsefAuthorizationStatus(status: boolean) {
      this.selectedCompany.ksef_authorized = status;
    },
  },
});
