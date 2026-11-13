<script setup lang="ts">
import { Button, DataTable, Column, Tag, useToast, type DataTableSortEvent } from "primevue";
import { ref, watch } from "vue";
import { useMutation } from "@tanstack/vue-query";

import {
  paymentStatus,
  paymentStatusSeverity,
  type invoiceTableType,
} from "../../../lib/types/invoices.ts";
import { formatLocalDate, formatPLN } from "../../../lib/utils.ts";
import { incomeTypes, costTypes } from "../../../lib/constants.ts";
import SaleCostInputDialog from "./AddSalesDialog.vue";
import { useCurrentUserStore } from "../../../stores/currentUserStore.ts";
import {
  getCashflowListLazy,
  type sortByOptions,
  type sortOrderOptions,
} from "../../../lib/services/cashflowDashboardService.ts";
import type { CashflowListItem } from "../../../lib/types/cashflow.ts";

const props = defineProps<{
  selectedYear: number;
  selectedMonth: number | null;
  type: invoiceTableType;
  monthSales: number | undefined;
  previusMonthSales: number | undefined;
  monthCosts: number | undefined;
  previousMonthCosts: number | undefined;
}>();

const toast = useToast();
const currentUserStore = useCurrentUserStore();

const selectedInvoice = ref(null);
const showSaleCostInputDialog = ref(false);
const cashflow = ref<number | undefined>(0);
const cashflowItems = ref<CashflowListItem[]>([]);
const previousMonthCashflow = ref<number | undefined>(0);
const percentageChange = ref<string | undefined>();

const currentOffset = ref(0);
const sortBy = ref<sortByOptions>(null);
const sortOrder = ref<sortOrderOptions>(null);
const hasMoreCashflowItems = ref(true);
const pageSize = 50;

function getCashflowQueryKey() {
  return JSON.stringify([
    currentUserStore.getCompanyId,
    props.selectedYear,
    props.selectedMonth,
    props.type,
    sortBy.value,
    sortOrder.value,
  ]);
}

const getMonthlyCashflowListLazyMutation = useMutation({
  mutationFn: async (request: { offset: number; queryKey: string }) => {
    const companyId = currentUserStore.getCompanyId;
    return await getCashflowListLazy(
      companyId!,
      props.selectedYear,
      props.selectedMonth,
      props.type,
      request.offset,
      pageSize,
      sortBy.value,
      sortOrder.value,
    );
  },

  onSuccess: (data, request) => {
    if (request.queryKey !== getCashflowQueryKey()) {
      return;
    }

    cashflowItems.value = request.offset === 0 ? data : [...cashflowItems.value, ...data];
    currentOffset.value = request.offset + data.length;
    hasMoreCashflowItems.value = data.length === pageSize;
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

function loadFirstCashflowPage() {
  currentOffset.value = 0;
  hasMoreCashflowItems.value = true;
  cashflowItems.value = [];
  getMonthlyCashflowListLazyMutation.mutate({ offset: 0, queryKey: getCashflowQueryKey() });
}

function loadNextCashflowPage() {
  if (!hasMoreCashflowItems.value || getMonthlyCashflowListLazyMutation.isPending.value) {
    return;
  }

  getMonthlyCashflowListLazyMutation.mutate({
    offset: currentOffset.value,
    queryKey: getCashflowQueryKey(),
  });
}

function onCashflowScroll(event: Event) {
  const scrollContainer = event.target as HTMLElement;
  if (
    scrollContainer.scrollHeight - scrollContainer.scrollTop - scrollContainer.clientHeight <=
    48
  ) {
    loadNextCashflowPage();
  }
}

function onInvoiceSelect(event: any) {
  selectedInvoice.value = event.data;
}

function onInvoiceUnselect() {
  selectedInvoice.value = null;
}

function onListSort(event: DataTableSortEvent) {
  sortBy.value = event.sortField === undefined ? null : (event.sortField as sortByOptions);

  if (event.sortOrder === null) {
    sortOrder.value = null;
  } else {
    sortOrder.value = event.sortOrder === 1 ? "asc" : "desc";
  }
  loadFirstCashflowPage();
}

function updatePercentageChange() {
  const current = cashflow.value;
  const previous = previousMonthCashflow.value;

  if (current === undefined || previous === undefined || previous === 0) {
    percentageChange.value = undefined;
    return;
  }

  const difference = ((current - previous) / previous) * 100;
  percentageChange.value = `${difference >= 0 ? "+" : ""}${difference.toFixed(2)}%`;
}

watch(
  [
    () => props.selectedYear,
    () => props.selectedMonth,
    () => props.type,
    () => props.monthSales,
    () => props.previusMonthSales,
    () => props.monthCosts,
    () => props.previousMonthCosts,
  ],
  () => {
    cashflow.value = props.type === "sales" ? props.monthSales : props.monthCosts;
    previousMonthCashflow.value =
      props.type === "sales" ? props.previusMonthSales : props.previousMonthCosts;
    updatePercentageChange();
    loadFirstCashflowPage();
  },
  { immediate: true },
);
</script>

<template>
  <div class="p-div-white flex flex-1 flex-col gap-2">
    <!-- CASHFLOW SUMMARY -->
    <div class="flex justify-between items-center">
      <div class="flex flex-1 flex-col gap-2">
        <h1 class="text-xl font-bold">
          {{ props.type === "sales" ? "Przychód netto" : "Koszty netto" }}
          {{ cashflow !== undefined ? formatPLN(cashflow) : "—" }}
        </h1>
        <div class="flex flex-1 gap-1">
          <h3 class="p-h3">vs poprzedni miesiąc:</h3>
          <h3
            :class="
              (percentageChange?.startsWith('+') && props.type === 'sales') ||
              (percentageChange?.startsWith('-') && props.type === 'purchases')
                ? 'text-green-600'
                : percentageChange
                  ? 'text-red-600'
                  : ''
            "
          >
            {{ percentageChange ?? "—" }}
          </h3>
        </div>
      </div>
      <!-- <Button
        v-tooltip.bottom="type === 'sales' ? 'Dodaj dane sprzedażowe' : 'Dodaj dane kosztowe'"
        icon="pi pi-plus"
        rounded
        @click="showSaleCostInputDialog = true"
      ></Button> -->
    </div>
    <!-- INVOICES BRIEF TABLE -->
    <div class="p-div-white flex flex-1 flex-col gap-2" @scroll.capture="onCashflowScroll">
      <DataTable
        v-model:selection="selectedInvoice"
        :value="cashflowItems"
        data-key="id"
        striped-rows
        selection-mode="single"
        removable-sort
        scrollable
        scroll-height="400px"
        @row-select="onInvoiceSelect"
        @row-unselect="onInvoiceUnselect"
        @sort="onListSort"
      >
        <Column field="issue_date" header="Data" sortable>
          <template #body="slotProps">
            {{ formatLocalDate(new Date(slotProps.data.issue_date)) }}
          </template></Column
        >
        <Column field="type" header="Typ" sortable>
          <template #body="slotProps">
            {{
              props.type === "sales"
                ? incomeTypes[slotProps.data.type]?.label
                : costTypes[slotProps.data.type]?.label
            }}
          </template>
        </Column>
        <Column
          field="contractor_name"
          :header="props.type === 'sales' ? 'Klient' : 'Dostawca'"
          sortable
        ></Column>
        <Column field="net_value" header="Wartość netto" sortable>
          <template #body="slotProps">
            {{ formatPLN(slotProps.data.net_value) }}
          </template>
        </Column>
        <Column field="payment_status" header="Status płatności" sortable>
          <template #body="slotProps">
            <div class="flex justify-end">
              <Tag
                :value="paymentStatus[slotProps.data.payment_status]"
                :severity="paymentStatusSeverity[slotProps.data.payment_status]"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>

  <SaleCostInputDialog
    :visible="showSaleCostInputDialog"
    :type="props.type"
    :loading="false"
    @update:visible="showSaleCostInputDialog = $event"
    @cancel="showSaleCostInputDialog = false"
  />
</template>
