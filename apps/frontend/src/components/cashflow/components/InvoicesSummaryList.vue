<script setup lang="ts">
import { Button, DataTable, Column, Tag } from "primevue";
import { ref, watch } from "vue";
import {
  paymentStatus,
  paymentStatusSeverity,
  type invoiceTableType,
} from "../../../lib/types/invoices";
import { formatPLN } from "../../../lib/utils";

import items from "../../../assets/mock_invoices";

import { incomeTypes, costTypes } from "../../../lib/constants";
import SaleCostInputDialog from "./AddSalesDialog.vue";

const props = defineProps<{
  selectedYear: number;
  selectedMonth: number | null;
  type: invoiceTableType;
  monthSales: number | undefined;
  previusMonthSales: number | undefined;
  monthCosts: number | undefined;
  previousMonthCosts: number | undefined;
}>();

const selectedInvoice = ref(null);
const showSaleCostInputDialog = ref(false);
const cashflow = ref<number | undefined>(0);
const previousMonthCashflow = ref<number | undefined>(0);
const percentageChange = ref<string | undefined>();

function onInvoiceSelect(event: any) {
  selectedInvoice.value = event.data;
}

function onInvoiceUnselect() {
  selectedInvoice.value = null;
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
      <Button
        v-tooltip.bottom="type === 'sales' ? 'Dodaj dane sprzedażowe' : 'Dodaj dane kosztowe'"
        icon="pi pi-plus"
        rounded
        @click="showSaleCostInputDialog = true"
      ></Button>
    </div>
    <!-- INVOICES BRIEF TABLE -->
    <div class="p-div-white flex flex-1 flex-col gap-2">
      <DataTable
        v-model:selection="selectedInvoice"
        :value="items"
        data-key="inv_nr"
        striped-rows
        selection-mode="single"
        removable-sort
        scrollable
        scroll-height="400px"
        @row-select="onInvoiceSelect"
        @row-unselect="onInvoiceUnselect"
      >
        <Column field="date" header="Data" sortable></Column>
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
          field="buyer"
          :header="props.type === 'sales' ? 'Klient' : 'Dostawca'"
          sortable
        ></Column>
        <Column field="sum_net" header="Wartość netto" sortable>
          <template #body="slotProps">
            {{ formatPLN(slotProps.data.sum_net) }}
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
