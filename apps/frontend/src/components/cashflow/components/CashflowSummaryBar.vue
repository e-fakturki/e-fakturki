<script setup lang="ts">
import { ref, watch } from "vue";
import { formatPLN } from "../../../lib/utils";
import { useMutation } from "@tanstack/vue-query";
import { useToast } from "primevue";
import { useCurrentUserStore } from "../../../stores/currentUserStore";
import { getMonthlySalesSummary } from "../../../lib/services/cashflowDashboardService";

const props = defineProps<{
  selectedYear: number;
  selectedMonth: number | null;
  monthlyProfit: number | undefined;
}>();

const toast = useToast();
const currentUserStore = useCurrentUserStore();

const profit = ref<number | undefined>(props.monthlyProfit);
const salesAmount = ref<number | null | undefined>(0);
const costAmount = ref<number | null | undefined>(0);
const averageSaleValue = ref<number | null | undefined>(0);
const averageCostValue = ref<number | null | undefined>(0);
const newClients = ref<number | null | undefined>(0);
const lostClients = ref<number | null | undefined>(0);
const invoicesNotPayed = ref<number | null | undefined>(0);
const costInvoicesNotPayed = ref<number | null | undefined>(0);

const getMonthlySalesSummaryMutation = useMutation({
  mutationFn: async () => {
    const companyId = currentUserStore.getCompanyId;
    return await getMonthlySalesSummary(companyId!, props.selectedYear, props.selectedMonth);
  },

  onSuccess: (data) => {
    salesAmount.value = data.sales_amount;
    costAmount.value = data.costs_amount;
    averageSaleValue.value = data.avg_sale_value;
    averageCostValue.value = data.avg_cost_value;
    newClients.value = data.new_customers;
    lostClients.value = data.inactive_customers;
    invoicesNotPayed.value = data.unpaid_sales;
    costInvoicesNotPayed.value = data.unpaid_costs;
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

watch(
  [() => props.selectedYear, () => props.selectedMonth, () => props.monthlyProfit],
  () => {
    getMonthlySalesSummaryMutation.mutate();
    profit.value = props.monthlyProfit;
  },
  { immediate: true },
);
</script>

<template>
  <div class="p-div-white flex flex-col gap-2">
    <!-- INVOICES SUMMARY -->
    <div class="flex flex-col gap-4 justify-start">
      <h1 class="text-xl font-bold">
        Potencjalny dochód netto {{ profit !== undefined ? formatPLN(profit!) : "-" }}
      </h1>
      <div class="flex w-full justify-between">
        <div class="flex flex-col gap-2">
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Ilość sprzedaży</h3>
            <h1 class="text-xl font-bold">
              {{ salesAmount }}
            </h1>
          </div>
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Ilość kosztów</h3>
            <h1 class="text-xl font-bold">
              {{ costAmount }}
            </h1>
          </div>
        </div>
        <div class="flex flex-col gap-2">
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Średnia wartość netto sprzedaży</h3>
            <h1 class="text-xl font-bold">
              {{ formatPLN(averageSaleValue) }}
            </h1>
          </div>
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Średnia wartość netto kosztu</h3>
            <h1 class="text-xl font-bold">
              {{ formatPLN(averageCostValue) }}
            </h1>
          </div>
        </div>
        <div class="flex flex-col gap-2">
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Nowi klienci (względem ostatniego miesiąca)</h3>
            <h1 class="text-xl font-bold">
              {{ newClients }}
            </h1>
          </div>
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Nieaktywni klienci (względem ostatniego miesiąca)</h3>
            <h1 class="text-xl font-bold">
              {{ lostClients }}
            </h1>
          </div>
        </div>
        <div class="flex flex-col gap-2">
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Zaległe płatności od klientów</h3>
            <h1 class="text-xl font-bold">
              {{ invoicesNotPayed }}
            </h1>
          </div>
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Zaległe płatności dla dostawców</h3>
            <h1 class="text-xl font-bold">
              {{ costInvoicesNotPayed }}
            </h1>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
