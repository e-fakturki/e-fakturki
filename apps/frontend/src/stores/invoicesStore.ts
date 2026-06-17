import { defineStore } from "pinia";

export const useInvoicesStore = defineStore("invoicesStore", {
  state: () => {
    return {
      newSalesInvoicesCount: 0,
      newPurchaseInvoicesCount: 0,
    };
  },
  getters: {
    getSalesInvoicesCount: (state) => state.newSalesInvoicesCount,
    getPurchaseInvoicesCount: (state) => state.newPurchaseInvoicesCount,
    getSalesInvoicesCountStr: (state) =>
      state.newSalesInvoicesCount > 0 ? `${state.newSalesInvoicesCount}` : "",
    getPurchaseInvoicesCountStr: (state) =>
      state.newPurchaseInvoicesCount > 0 ? `${state.newPurchaseInvoicesCount}` : "",
  },
  actions: {
    setSalesInvoicesCount(count: number) {
      this.newSalesInvoicesCount = count;
    },
    setPurchaseInvoicesCount(count: number) {
      this.newPurchaseInvoicesCount = count;
    },
  },
});
