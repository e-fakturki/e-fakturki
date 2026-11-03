<script setup lang="ts">
import { Button, Dialog, useToast, Tag } from "primevue";
import { DataTable, Column } from "primevue";
import { incomeTypes, costTypes } from "../../../lib/constants";
import { formatPLN } from "../../../lib/utils";

import {
  paymentStatus,
  paymentStatusSeverity,
  type invoiceTableType,
} from "../../../lib/types/invoices";
import { onMounted, ref } from "vue";
import type { TaxRate } from "../../../lib/types/products";
import DeleteConfirmDialog from "../../dialogs/DeleteConfirmDialog.vue";
import type { NewCashflowRecord } from "../../../lib/types/cashflow";
import NewSaleInputDialog from "./NewSaleInputDialog.vue";
import { useMutation } from "@tanstack/vue-query";
import { getTaxRates } from "../../../lib/services/productService.ts";

const props = defineProps<{
  visible: boolean;
  type: invoiceTableType;
  loading?: boolean;
}>();

const emit = defineEmits(["update:visible", "success", "cancel"]);

const toast = useToast();

const taxRates = ref<TaxRate[]>([]);
const taxRateMap = ref<Map<string, TaxRate>>(new Map());
const newData = ref<NewCashflowRecord[]>([]);
const expandedRows = ref<{ [key: string]: boolean }>({});
const recordToEdit = ref<NewCashflowRecord | null>(null);
const newRecordDialog = ref(false);
const editRecordDialog = ref(false);
const deleteRecordDialog = ref(false);

const getTaxRatesMutation = useMutation({
  mutationFn: async () => {
    return await getTaxRates();
  },

  onSuccess: (data) => {
    taxRates.value = data;
    taxRateMap.value = new Map(data.map((tax) => [tax.str_repr, tax]));
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

function onRowSelect(event: any) {
  recordToEdit.value = null;
  recordToEdit.value = event.data;
  editRecordDialog.value = true;
}

function onRowUnselect() {
  recordToEdit.value = null;
  editRecordDialog.value = false;
}

function onNewRecordAdded(record: NewCashflowRecord) {
  const existingRecordIndex = newData.value.findIndex(
    (recordLocal) => recordLocal.id === record.id,
  );

  if (existingRecordIndex >= 0) {
    newData.value[existingRecordIndex] = record;
  } else {
    newData.value.push(record);
  }
}

function deleteRecord(record: NewCashflowRecord | null) {
  if (record) {
    newData.value = newData.value.filter((r) => r.id !== record.id);
    recordToEdit.value = null;
    deleteRecordDialog.value = false;
  }
}

onMounted(() => {
  getTaxRatesMutation.mutate();
});
</script>

<template>
  <Dialog
    :visible="visible"
    @update:visible="emit('update:visible', $event)"
    modal
    :draggable="false"
    :style="{ width: '60rem', height: '50rem' }"
    :contentStyle="{ display: 'flex', flexDirection: 'column', minHeight: '0', overflow: 'hidden' }"
  >
    <template #header>
      <div class="flex flex-col text-xl font-semibold">
        <span>
          {{ props.type === "sales" ? "Dodaj dane sprzedażowe" : "Dodaj dane kosztowe" }}
        </span>
      </div>
    </template>
    <div class="flex flex-1 flex-col min-h-0 overflow-hidden card justify-center pt-2">
      <div class="p-div-grey flex flex-1 min-h-0 min-w-0 flex-col gap-2">
        <DataTable
          :value="newData"
          dataKey="id"
          v-model:expanded-rows="expandedRows"
          v-model:selection="recordToEdit"
          selection-mode="single"
          @row-select="onRowSelect"
          @row-unselect="onRowUnselect"
          removableSort
          scrollable
          scrollHeight="flex"
          class="flex-1 min-h-0"
        >
          <template #header>
            <div class="flex justify-between items-center text-l font-semibold">
              <span>
                {{ props.type === "sales" ? "Nowe dane sprzedażowe" : "Nowe dane kosztowe" }}
              </span>
              <Button
                label="Dodaj wiersz"
                icon="pi pi-plus"
                @click="newRecordDialog = true"
                :disabled="getTaxRatesMutation.isPending.value"
              />
            </div>
          </template>
          <template #empty> Brak nowych rekordów, dodaj wiersz lub załaduj plik CSV. </template>
          <Column expander style="width: 1%"></Column>
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
            field="name"
            :header="props.type === 'sales' ? 'Nazwa pozycji/klienta' : 'Nazwa pozycji/dostawcy'"
            sortable
          ></Column>
          <Column field="netValue" header="Wartość netto" sortable>
            <template #body="slotProps">
              {{ formatPLN(slotProps.data.netValue) }}
            </template>
          </Column>
          <Column style="width: 1%">
            <template #body="slotProps">
              <Button
                icon="pi pi-trash"
                variant="outlined"
                severity="danger"
                @click="
                  () => {
                    recordToEdit = null;
                    recordToEdit = slotProps.data;
                    deleteRecordDialog = true;
                  }
                "
              /> </template
          ></Column>
          <template #expansion="slotProps">
            <div class="flex flex-1 gap-4 pl-15">
              <div class="flex min-w-0 flex-1 flex-col">
                <span class="font-semibold">Opis</span>
                <span class="break-words">{{ slotProps.data.description || "-" }}</span>
              </div>
              <div class="flex min-w-0 flex-1 flex-col">
                <span class="font-semibold">Stawka VAT</span>
                <span class="break-words">{{
                  taxRateMap.get(slotProps.data.taxRate)?.display_text || "-"
                }}</span>
              </div>
              <div class="flex min-w-0 flex-1 flex-col">
                <span class="font-semibold">Status płatności</span>
                <div>
                  <Tag
                    :value="paymentStatus[slotProps.data.paymentStatus]"
                    :severity="paymentStatusSeverity[slotProps.data.paymentStatus]"
                  />
                </div>
              </div>
            </div>
          </template>
        </DataTable>
      </div>
      <!-- Action buttons -->
      <div class="flex justify-between pt-4">
        <div class="flex justify-start gap-4">
          <Button disabled label="Załaduj CSV" severity="secondary" @click="emit('cancel')" />
          <Button
            disabled
            label="Pobierz wzór pliku CSV"
            severity="secondary"
            @click="emit('cancel')"
          />
        </div>
        <div class="flex justify-end gap-4">
          <Button label="Anuluj" severity="secondary" class="sm:w-30" @click="emit('cancel')" />
          <Button
            label="Zapisz"
            severity="secondary"
            class="sm:w-30"
            @click="emit('success', selectedValue)"
          />
        </div>
      </div>
    </div>
  </Dialog>

  <!-- New record input dialog -->
  <NewSaleInputDialog
    :visible="newRecordDialog"
    :type="props.type"
    createOrUpdate="create"
    :recordInfo="null"
    :taxRates="taxRates"
    :loading="getTaxRatesMutation.isPending.value"
    @update:visible="newRecordDialog = $event"
    @cancel="newRecordDialog = false"
    @success="onNewRecordAdded"
  />

  <!-- Edit record input dialog -->
  <NewSaleInputDialog
    :visible="editRecordDialog"
    :type="props.type"
    createOrUpdate="update"
    :recordInfo="recordToEdit"
    :taxRates="taxRates"
    :loading="getTaxRatesMutation.isPending.value"
    @update:visible="editRecordDialog = $event"
    @cancel="onRowUnselect"
    @success="onNewRecordAdded"
  />

  <!-- Record delete dialog -->
  <DeleteConfirmDialog
    v-model:visible="deleteRecordDialog"
    :deletionObjectName="recordToEdit?.name"
    deleteObjectString="rekord"
    @confirm="deleteRecord(recordToEdit)"
    @cancel="deleteRecordDialog = false"
  />
</template>
