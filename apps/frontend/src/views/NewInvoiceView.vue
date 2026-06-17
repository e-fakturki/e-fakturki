<script setup lang="ts">
import {
  DataTable,
  Column,
  Button,
  InputText,
  Select,
  DatePicker,
  Divider,
  useToast,
  Panel,
  InputNumber,
} from "primevue";

import { useCurrentUserStore } from "../stores/currentUserStore";
import { computed, onMounted, ref } from "vue";
import type { InvoiceObject, InvoiceEntry } from "../lib/types/invoices";
import {
  calculateGrossPrice,
  calculateGrossTotal,
  calculateNetTotal,
  calculateTaxTotal,
  formatPLN,
  roundTo2,
  verifyEntriesTotals,
  verifyInvoiceTotals,
  verifyNetVsGrossPrice,
} from "../lib/utils";
import { useMutation } from "@tanstack/vue-query";
import { getTaxRates } from "../lib/services/productService";
import type { TaxRate } from "../lib/types/products";
import InvoiceCreationFooter from "../components/invoices/InvoiceCreationFooter.vue";
import InvoiceCreationCompanyDataForm from "../components/invoices/InvoiceCreationCompanyDataForm.vue";
import InvoiceCreationInfoForm from "../components/invoices/InvoiceCreationInfoForm.vue";
import InvoiceDetails from "../components/invoices/InvoiceDetails.vue";
import InvoiceCreationPaymentDetails from "../components/invoices/InvoiceCreationPaymentDetails.vue";
import { saveCreatedInvoice } from "../lib/services/invoiceService.ts";
import { postInvoiceToKsef } from "../lib/services/ksefService.ts";

const toast = useToast();
const currentUserStore = useCurrentUserStore();

const invoice = ref<InvoiceObject>({
  invoice_number: "",
  invoice_type: "VAT",
  ksef_status: "not_sent",
  is_new: true,
  issue_date: "",
  issue_place: "",
  seller_info: {
    name: "",
    nip: "",
    krs: "",
    regon: "",
    country_code: "",
    address_l1: "",
    address_l2: "",
    address_correspondance_l1: "",
    address_correspondance_l2: "",
    email: "",
    phone_number: "",
  },
  buyer_info: {
    name: "",
    nip: "",
    krs: "",
    regon: "",
    country_code: "",
    address_l1: "",
    address_l2: "",
    address_correspondance_l1: "",
    address_correspondance_l2: "",
    email: "",
    phone_number: "",
  },
  entries: [],
  currency: "PLN",
  net_total: 0,
  tax_total: 0,
  gross_total: 0,
  payment: {
    payment_status: "",
    payment_type: "",
    payment_date: null,
    payment_due_date: null,
    partial_payments: null,
    seller_bank_account_number: null,
    seller_bank_name: null,
  },
  id: null,
  ksef_number: null,
  invoicing_date: null,
  acquisition_date: null,
  permanent_storage_date: null,
  annotations: null,
  additional_info: null,
  footer_info: null,
  footer_registers: null,
});
const invoiceEntryColumns = ref([
  { field: "delete_row", header: "", width: "width: 5%", readonly: true },
  { field: "row_number", header: "Nr. wiersza", width: "width: 5%", readonly: true },
  { field: "delivery_date", header: "Dostawa", width: "width: 8%", readonly: false },
  { field: "name", header: "Nazwa", width: "width: 17%", readonly: false },
  { field: "unit", header: "Jedn. Miary", width: "width: 6%", readonly: false },
  { field: "amount", header: "Ilość", width: "width: 6%", readonly: false },
  { field: "net_price", header: "Cena netto", width: "width: 8%", readonly: false },
  { field: "tax_rate", header: "Stawka VAT", width: "width: 8%", readonly: false },
  { field: "gross_price", header: "Cena brutto", width: "width: 8%", readonly: true },
  { field: "net_total", header: "Wartość netto", width: "width: 8%", readonly: true },
  { field: "tax_total", header: "Wartość VAT", width: "width: 8%", readonly: true },
  { field: "gross_total", header: "Wartość brutto", width: "width: 8%", readonly: true },
]);
const taxRates = ref<TaxRate[]>([]);
const taxRateMap = ref<Map<string, TaxRate>>(new Map());
const invoicePreviewDialog = ref(false);

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

const saveInvoiceMutation = useMutation({
  mutationFn: async () => {
    return await saveCreatedInvoice(invoice.value, currentUserStore.getCompanyId);
  },

  onSuccess: (data) => {
    toast.add({ severity: "success", summary: "Poprawnie utworzono fakturę.", life: 5000 });
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

const saveInvoiceandUploadToKsefMutation = useMutation({
  mutationFn: async () => {
    return await postInvoiceToKsef(invoice.value, currentUserStore.getCompanyId);
  },

  onSuccess: (data) => {
    toast.add({ severity: "success", summary: "Poprawnie wysłano fakturę do KSeF.", life: 5000 });
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

const formsDisabled = computed(
  () => saveInvoiceMutation.isPending.value || saveInvoiceandUploadToKsefMutation.isPending.value,
);

function newEntry() {
  invoice.value?.entries.push({
    row_number: invoice.value?.entries.length + 1,
    delivery_date: new Date(),
    name: "",
    amount: 1,
    unit: "",
    net_price: 0,
    gross_price: 0,
    tax_rate: taxRates.value[0]?.str_repr,
    net_total: 0,
    tax_total: 0,
    gross_total: 0,
  });
}

function recalculateInvoiceTotals() {
  invoice.value.net_total = roundTo2(
    invoice.value.entries.reduce((acc, entry) => acc + entry.net_total, 0),
  );
  invoice.value.tax_total = roundTo2(
    invoice.value.entries.reduce((acc, entry) => acc + entry.tax_total, 0),
  );
  invoice.value.gross_total = roundTo2(
    invoice.value.entries.reduce((acc, entry) => acc + entry.gross_total, 0),
  );
}

function onCellEditComplete(event: any) {
  const { data, newValue, field } = event;

  // optional validation
  if (newValue === null || newValue === undefined) {
    event.preventDefault();
    return;
  }

  // recalculate individual record prices and totals
  if (field === "net_price" && Number(newValue) > 0) {
    data[field] = roundTo2(Number(newValue));
    data.gross_price = calculateGrossPrice(
      data.net_price,
      taxRateMap.value.get(data.tax_rate)?.value,
    );
    data.net_total = calculateNetTotal(data.net_price, data.amount);
    data.tax_total = calculateTaxTotal(
      data.net_price,
      taxRateMap.value.get(data.tax_rate)?.value,
      data.amount,
    );
    data.gross_total = calculateGrossTotal(
      data.net_price,
      data.amount,
      taxRateMap.value.get(data.tax_rate)?.value,
    );
  }
  if (field === "amount" && Number(newValue) > 0) {
    data[field] = roundTo2(Number(newValue));
    data.net_total = calculateNetTotal(data.net_price, data.amount);
    data.tax_total = calculateTaxTotal(
      data.net_price,
      taxRateMap.value.get(data.tax_rate)?.value,
      data.amount,
    );
    data.gross_total = calculateGrossTotal(
      data.net_price,
      data.amount,
      taxRateMap.value.get(data.tax_rate)?.value,
    );
  }
  if (field === "tax_rate") {
    data[field] = newValue;
    data.gross_price = calculateGrossPrice(
      data.net_price,
      taxRateMap.value.get(data.tax_rate)?.value,
    );
    data.tax_total = calculateTaxTotal(
      data.net_price,
      taxRateMap.value.get(data.tax_rate)?.value,
      data.amount,
    );
    data.gross_total = calculateGrossTotal(
      data.net_price,
      data.amount,
      taxRateMap.value.get(data.tax_rate)?.value,
    );
  }

  data[field] = newValue;

  // recalculate invoice totals
  recalculateInvoiceTotals();
}

function removeInvoiceEntry(entry: InvoiceEntry) {
  invoice.value.entries = invoice.value?.entries.filter(
    (record) => record.row_number !== entry.row_number,
  );

  // move row numbers
  invoice.value.entries.forEach((e, index) => {
    e.row_number = index + 1;
  });

  // recalculate invoice totals
  recalculateInvoiceTotals();
}

function updateInvoiceInfo(event: any) {
  invoice.value.invoice_number = event.invoiceNumber;
  invoice.value.issue_place = event.issuePlace;
  invoice.value.issue_date = event.invoiceDate.toLocaleString();
}

function updateInvoicePayment(event: any) {
  invoice.value.payment.payment_status = event.paymentStatus;
  invoice.value.payment.payment_date = event.paymentDate
    ? event.paymentDate.toLocaleString()
    : null;
  invoice.value.payment.payment_due_date = event.paymentDueDate
    ? event.paymentDueDate.toLocaleString()
    : null;
  invoice.value.payment.payment_type = event.paymentType;
  invoice.value.payment.seller_bank_account_number = event.iban;
  invoice.value.payment.seller_bank_name = event.bankName;
}

function updateInvoiceCompaniesInfo(event: any, company: "buyer" | "seller") {
  if (company === "buyer") {
    invoice.value.buyer_info.name = event.name;
    invoice.value.buyer_info.nip = event.nip;
    invoice.value.buyer_info.krs = event.krs;
    invoice.value.buyer_info.regon = event.regon;
    invoice.value.buyer_info.country_code = event.countryCode;
    invoice.value.buyer_info.address_l1 = event.addressL1;
    invoice.value.buyer_info.address_l2 = event.addressL2;
    invoice.value.buyer_info.address_correspondance_l1 = event.addressCorrespondanceL1;
    invoice.value.buyer_info.address_correspondance_l2 = event.addressCorrespondanceL2;
    invoice.value.buyer_info.email = event.email;
    invoice.value.buyer_info.phone_number = event.phoneNumber;
  } else {
    invoice.value.seller_info.name = event.name;
    invoice.value.seller_info.nip = event.nip;
    invoice.value.seller_info.krs = event.krs;
    invoice.value.seller_info.regon = event.regon;
    invoice.value.seller_info.country_code = event.countryCode;
    invoice.value.seller_info.address_l1 = event.addressL1;
    invoice.value.seller_info.address_l2 = event.addressL2;
    invoice.value.seller_info.address_correspondance_l1 = event.addressCorrespondanceL1;
    invoice.value.seller_info.address_correspondance_l2 = event.addressCorrespondanceL2;
    invoice.value.seller_info.email = event.email;
    invoice.value.seller_info.phone_number = event.phoneNumber;
  }
}

const invoiceInfoFormRef = ref();
const invoiceSellerFormRef = ref();
const invoiceBuyerFormRef = ref();
const invoicePaymentFormRef = ref();

function onClearInvoiceData() {
  invoiceInfoFormRef.value.reset();
  invoiceSellerFormRef.value.reset();
  invoiceBuyerFormRef.value.reset();
  invoicePaymentFormRef.value.reset();

  invoice.value.entries = [];
  recalculateInvoiceTotals();
}

async function validate_fields() {
  // validate all forms
  const validationResults = await Promise.all([
    invoiceInfoFormRef.value.validate(),
    invoiceSellerFormRef.value.validate(),
    invoiceBuyerFormRef.value.validate(),
    invoicePaymentFormRef.value.validate(),
  ]);
  if (validationResults.some((result) => !result)) {
    return false;
  }

  // validate invoice entries
  // ensure there is at least one invoice entry
  if (!invoice.value.entries || invoice.value.entries.length === 0) {
    toast.add({ severity: "error", summary: "Brak pozycji na fakturze.", life: 5000 });
    return false;
  }

  // ensure no entry has null/undefined/empty/0/negative values
  const hasNullValue = invoice.value.entries.some((entry) => {
    return Object.keys(entry).some(
      (key) =>
        entry[key] === null ||
        entry[key] === undefined ||
        entry[key] === "" ||
        entry[key] === 0 ||
        (Number(entry[key]) && entry[key] < 0),
    );
  });
  if (hasNullValue) {
    toast.add({
      severity: "error",
      summary: "Pozycje na fakturze zawierają puste pola lub nieprawidłowe ceny.",
      life: 5000,
    });
    return false;
  }

  // ensure every entry is calculated correctly
  const hasInvalidEntry = invoice.value.entries.some((entry) => {
    return !(
      verifyNetVsGrossPrice(
        entry.net_price,
        entry.gross_price,
        taxRateMap.value.get(entry.tax_rate.str_repr)?.value,
      ) &&
      verifyEntriesTotals(entry) &&
      verifyInvoiceTotals(invoice.value)
    );
  });
  if (hasInvalidEntry) {
    toast.add({
      severity: "error",
      summary: "Pozycje na fakturze są błędnie obliczone, spróbuj stworzyć pozycje ponownie.",
      life: 5000,
    });
    return false;
  }

  return true;
}

async function onInvoicePreview() {
  if (!(await validate_fields())) {
    return;
  }

  invoicePreviewDialog.value = true;
}

async function onInvoiceSave() {
  if (!(await validate_fields())) {
    return;
  }

  saveInvoiceMutation.mutate();
}

async function onInvoiceUploadToKsef() {
  if (!(await validate_fields())) {
    return;
  }

  saveInvoiceandUploadToKsefMutation.mutate();
}

onMounted(async () => {
  await getTaxRatesMutation.mutateAsync();
});
</script>

<template>
  <!-- header -->
  <div class="flex flex-col mt-5 mb-3 gap-1">
    <span class="text-xl font-bold pl-4 text-color">Tworzenie nowej faktury</span>
    <Divider />
  </div>
  <!-- invoice contents -->
  <Panel class="px-24 h-826/1000 flex flex-1 flex-col overflow-y-scroll">
    <!-- <div class="gap-4 px-12 h-4/5 overflow-y-scroll"> -->
    <div class="flex flex-1 pb-4 justify-center">
      <InvoiceCreationInfoForm
        ref="invoiceInfoFormRef"
        :disabled="formsDisabled"
        @update="updateInvoiceInfo"
      />
    </div>
    <!-- companies info -->
    <div class="flex flex-1 justify-between pb-12">
      <InvoiceCreationCompanyDataForm
        ref="invoiceSellerFormRef"
        :seller="true"
        :disabled="formsDisabled"
        @update="updateInvoiceCompaniesInfo($event, 'seller')"
      />
      <InvoiceCreationCompanyDataForm
        ref="invoiceBuyerFormRef"
        :seller="false"
        :disabled="formsDisabled"
        @update="updateInvoiceCompaniesInfo($event, 'buyer')"
      />
    </div>

    <!-- invoice entries table -->
    <DataTable
      :value="invoice?.entries"
      dataKey="row_number"
      editMode="cell"
      @cell-edit-complete="onCellEditComplete"
      :pt="{
        table: { style: 'table-layout: fixed;' },
        column: {
          bodycell: ({ state }) => ({
            class: [{ '!py-0': state['d_editing'] }],
          }),
        },
      }"
    >
      <template #header>
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="font-bold">Pozycje</span>
        </div>
      </template>
      <Column
        v-for="col of invoiceEntryColumns"
        :key="col.field"
        :field="col.field"
        :header="col.header"
        :editor="!col.readonly"
        :style="col.width"
      >
        <!-- NORMAL DISPLAY -->
        <template #body="{ data, field }">
          <div v-if="['delete_row'].includes(field)" class="flex flex-1 justify-center">
            <Button
              icon="pi pi-trash"
              variant="outlined"
              severity="danger"
              rounded
              raised
              @click="removeInvoiceEntry(data)"
              :disabled="formsDisabled"
            />
          </div>

          <span v-else-if="['row_number'].includes(field)">
            {{ data[field] }}
          </span>

          <!-- monetary values -->
          <InputNumber
            v-else-if="['net_price'].includes(field)"
            v-model="data[field]"
            mode="currency"
            currency="PLN"
            locale="pl-PL"
            autofocus
            fluid
            :disabled="formsDisabled"
          />

          <span
            v-else-if="['gross_price', 'net_total', 'tax_total', 'gross_total'].includes(field)"
          >
            {{ formatPLN(data[field]) }}
          </span>

          <!-- delivery date -->
          <span v-else-if="field === 'delivery_date'">
            <DatePicker
              v-model="data[field]"
              dateFormat="yy/mm/dd"
              fluid
              @click.stop
              @mousedown.stop
              :disabled="formsDisabled"
            />
          </span>

          <!-- tax rate -->
          <span
            v-else-if="field === 'tax_rate'"
            v-tooltip.bottom="taxRateMap.get(data[field])?.hint_text"
            >{{ taxRateMap.get(data[field])?.display_text || data[field] }}</span
          >

          <!-- default -->
          <InputText v-else v-model="data[field]" autofocus fluid :disabled="formsDisabled" />
        </template>

        <!-- EDIT MODE -->
        <template #editor="{ data, field }">
          <!-- row number -->
          <template v-if="field === 'row_number'">
            <span>{{ data[field] }}</span>
          </template>

          <!-- tax rate -->
          <template v-else-if="field === 'tax_rate'">
            <Select
              v-model="data[field]"
              :options="[...taxRateMap.keys()]"
              class="h-10.5"
              emptyMessage="Brak opcji do wyboru"
              fluid
              :disabled="formsDisabled"
            >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center gap-2">
                  <div
                    v-tooltip.bottom="taxRateMap.get(slotProps.value)?.hint_text"
                    class="flex flex-1"
                  >
                    {{ taxRateMap.get(slotProps.value)?.display_text }}
                  </div>
                </div>
                <span v-else>
                  {{ slotProps.placeholder }}
                </span>
              </template>
              <template #option="slotProps">
                <div class="flex flex-1 items-center gap-2">
                  <div
                    v-tooltip.bottom="taxRateMap.get(slotProps.option)?.hint_text"
                    class="flex flex-1"
                  >
                    {{ taxRateMap.get(slotProps.option)?.display_text }}
                  </div>
                </div>
              </template>
            </Select>
          </template>

          <!-- delivery date -->
          <template v-else-if="field === 'delivery_date'">
            <DatePicker
              v-model="data[field]"
              dateFormat="yy/mm/dd"
              fluid
              @click.stop
              @mousedown.stop
              :disabled="formsDisabled"
            />
          </template>

          <!-- product name -->
          <template v-else-if="['name', 'unit'].includes(field)">
            <InputText v-model="data[field]" autofocus fluid :disabled="formsDisabled" />
          </template>

          <!-- amount -->
          <template v-else-if="field === 'amount'">
            <InputNumber
              v-model="data[field]"
              locale="pl-PL"
              :minFractionDigits="0"
              :maxFractionDigits="3"
              autofocus
              fluid
              :disabled="formsDisabled"
            />
          </template>

          <!-- monetary values -->
          <template v-else-if="['net_price'].includes(field)">
            <InputNumber
              v-model="data[field]"
              mode="currency"
              currency="PLN"
              locale="pl-PL"
              autofocus
              fluid
              :disabled="formsDisabled"
            />
          </template>

          <!-- default -->
          <template v-else>
            <span>{{ formatPLN(data[field]) }}</span>
          </template>
        </template>

        <!-- FOOTER -->
        <template #footer>
          <Button
            v-if="col.field === 'delete_row'"
            class="ml-2"
            icon="pi pi-plus"
            rounded
            raised
            v-tooltip.bottom="'Dodaj kolejną pozycję'"
            @click="newEntry"
            :disabled="formsDisabled"
          ></Button>

          <span v-if="col.field === 'gross_price'" class="font-semibold"> SUMA: </span>
          <span v-else-if="col.field === 'net_total'" class="font-semibold">
            {{ formatPLN(invoice?.net_total || 0) }}
          </span>
          <span v-else-if="col.field === 'tax_total'" class="font-semibold">
            {{ formatPLN(invoice?.tax_total || 0) }}
          </span>
          <span v-else-if="col.field === 'gross_total'" class="font-semibold">
            {{ formatPLN(invoice?.gross_total || 0) }}
          </span>
        </template>
      </Column>
    </DataTable>

    <!-- payment details -->
    <div class="flex flex-1 justify-between pt-12">
      <InvoiceCreationPaymentDetails
        ref="invoicePaymentFormRef"
        :disabled="formsDisabled"
        @update="updateInvoicePayment"
      />
      <div>
        <span class="text-xl font-bold">Do zapłaty: </span>
        <span class="text-xl font-bold">{{ formatPLN(invoice?.gross_total || 0) }}</span>
      </div>
    </div>
    <!-- </div> -->
  </Panel>
  <!-- footer -->
  <div class="mt-3 relative">
    <InvoiceCreationFooter
      :disabled="formsDisabled"
      @preview="onInvoicePreview"
      @clear="onClearInvoiceData"
      @save="onInvoiceSave"
      @save-and-send="onInvoiceUploadToKsef"
    />
  </div>
  <!-- Invoice details dialog -->
  <InvoiceDetails
    v-model:visible="invoicePreviewDialog"
    :invoice="invoice"
    invoice_type="sales"
    :invoice_creation="true"
  />
</template>
