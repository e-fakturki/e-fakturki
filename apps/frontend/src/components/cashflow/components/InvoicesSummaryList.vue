<script setup lang="ts">
import { Button, DataTable, Column, Tag } from "primevue";
import { computed, ref } from "vue";
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
}>();

const selectedInvoice = ref(null);
const showSaleCostInputDialog = ref(false);

function onInvoiceSelect(event: any) {
  selectedInvoice.value = event.data;
}

function onInvoiceUnselect() {
  selectedInvoice.value = null;
}

// Randomly generated cashflow values for demonstration purposes
const cashflow = Math.floor(Math.random() * 10000);
const previousCashflow = Math.floor(cashflow * 0.9);

const calculateAgainstPreviousMonth = computed(() => {
  // Calculate the percentage difference with a + or - sign
  const difference = ((cashflow - previousCashflow) / previousCashflow) * 100;
  return (difference >= 0 ? "+" : "") + difference.toFixed(2);
});
</script>

<template>
  <div class="p-div-white flex flex-1 flex-col gap-2">
    <!-- CASHFLOW SUMMARY -->
    <div class="flex justify-between items-center">
      <div class="flex flex-1 flex-col gap-2">
        <h1 class="text-xl font-bold">
          {{ props.type === "sales" ? "Przychód netto" : "Koszty netto" }} {{ formatPLN(cashflow) }}
        </h1>
        <div class="flex flex-1 gap-1">
          <h3 class="p-h3">vs poprzedni miesiąc:</h3>
          <h3
            :class="
              (calculateAgainstPreviousMonth.startsWith('+') && props.type === 'sales') ||
                (calculateAgainstPreviousMonth.startsWith('-') && props.type === 'purchases')
                ? 'text-green-600'
                : 'text-red-600'
            "
          >
            {{ calculateAgainstPreviousMonth }}%
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
