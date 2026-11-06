<script setup lang="ts">
import {
  DatePicker,
  Button,
  Dialog,
  Message,
  InputText,
  InputNumber,
  FloatLabel,
  Select,
} from "primevue";
import { Form, FormField, type FormSubmitEvent } from "@primevue/forms";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import z from "zod";
import { onMounted, reactive, ref, watch } from "vue";

import { incomeTypes, costTypes } from "../../../lib/constants";
import type { IncomeType, NewCashflowRecord, PaymentStatusType } from "../../../lib/types/cashflow";
import type { CreateOrUpdate } from "../../../lib/types/company.ts";
import type { invoiceTableType } from "../../../lib/types/invoices";
import type { TaxRate } from "../../../lib/types/products";
import { paymentStatus } from "../../../lib/types/invoices";
import { formatLocalDate } from "../../../lib/utils.ts";

const props = defineProps<{
  visible: boolean;
  type: invoiceTableType;
  createOrUpdate: CreateOrUpdate;
  recordInfo: NewCashflowRecord | null;
  taxRates?: TaxRate[];
  loading?: boolean;
}>();

const emit = defineEmits(["update:visible", "success", "cancel"]);
const emitRecord = (record: NewCashflowRecord) => {
  emit("success", record);
};

const editOrAddText = props.createOrUpdate === "create" ? "Dodaj nową" : "Edytuj";
const typeOptions = ref<IncomeType[]>([]);
const paymentStatusOptions = ref<PaymentStatusType[]>([]);
const submitDisabled = ref(false);
const selectedType = ref<IncomeType | null | undefined>(null);
const selectedTaxRate = ref<TaxRate | null | undefined>(null);
const selectedDate = ref<Date | null | undefined>(new Date());
const selectedPaymentStatus = ref<PaymentStatusType | null | undefined>(null);

const initialValues = reactive({
  name: "",
  description: "",
  netValue: 0,
});

function resetInitialValues() {
  initialValues.name = props.recordInfo?.name ?? "";
  initialValues.description = props.recordInfo?.description ?? "";
  initialValues.netValue = props.recordInfo?.netValue ?? 0;
  selectedDate.value = props.recordInfo?.date ? new Date(props.recordInfo.date) : new Date();
}

function getTypesMockMutation(type: invoiceTableType) {
  // Mock implementation for fetching types based on the invoice type

  typeOptions.value = Object.entries(type === "sales" ? incomeTypes : costTypes).map(
    ([value, option]) => ({
      value,
      ...option,
    }),
  );

  // Filter out faktury (user shouldnt be able to add an invoice manually they are always fetched from KSeF)
  typeOptions.value = typeOptions.value.filter((option) => option.value !== "invoice");

  selectedType.value = typeOptions.value.find((option) => option.value === "other") ?? null;
}

function getPaymentStatusesMockMutation() {
  // Mock implementation for fetching payment statuses based on the invoice type

  paymentStatusOptions.value = Object.entries(paymentStatus).map(([value, label]) => ({
    value,
    label,
  }));

  selectedPaymentStatus.value =
    paymentStatusOptions.value.find((option) => option.value === "unpaid") ?? null;
}

const resolver = zodResolver(
  z.object({
    name: z
      .string()
      .min(1, { message: "Nazwa jest wymagana." })
      .max(255, { message: "Nazwa przekracza maksymalny rozmiar." }),
    description: z.string().max(2048, { message: "Opis przekracza maksymalny rozmiar." }),
    netValue: z
      .number({ message: "Cena netto musi być liczbą." })
      .min(0, { message: "Cena netto musi być nieujemna." }),
  }),
);

const onFormSubmit = async (event: FormSubmitEvent) => {
  const { valid } = event;
  if (!valid) return;

  if (
    !selectedType.value ||
    !selectedTaxRate.value ||
    !selectedPaymentStatus.value ||
    !selectedDate.value
  ) {
    return;
  }

  const newCashflowRecord: NewCashflowRecord = {
    id: props.createOrUpdate === "create" ? crypto.randomUUID() : props.recordInfo!.id,
    type: selectedType.value.value,
    date: formatLocalDate(selectedDate.value),
    name: event.values.name,
    description: event.values.description,
    netValue: event.values.netValue,
    taxRate: selectedTaxRate.value.str_repr,
    paymentStatus: selectedPaymentStatus.value.value,
  };

  submitDisabled.value = true;
  emitRecord(newCashflowRecord);
  emit("update:visible", false);
  submitDisabled.value = false;
};

watch(
  () => props.visible,
  async (visible) => {
    if (visible) {
      resetInitialValues();
      if (props.createOrUpdate === "update") {
        selectedTaxRate.value = props.taxRates!.find(
          (tax) => tax.str_repr === props.recordInfo?.taxRate,
        );
        selectedType.value = typeOptions.value.find(
          (option) => option.value === props.recordInfo?.type,
        );
        selectedPaymentStatus.value = paymentStatusOptions.value.find(
          (option) => option.value === props.recordInfo?.paymentStatus,
        );
      } else {
        selectedTaxRate.value = props.taxRates!.find((c) => c.str_repr === "23");
        selectedType.value = typeOptions.value.find((option) => option.value === "other") ?? null;
        selectedPaymentStatus.value =
          paymentStatusOptions.value.find((option) => option.value === "unpaid") ?? null;
      }
    }
  },
  { immediate: true },
);

onMounted(() => {
  getTypesMockMutation(props.type);
  getPaymentStatusesMockMutation();
});
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    :draggable="false"
    :style="{ width: '40rem' }"
    :content-style="{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '0',
      overflow: 'hidden',
    }"
    @update:visible="emit('update:visible', $event)"
  >
    <template #header>
      <div class="flex flex-col text-xl font-semibold">
        <span>
          {{
            props.type === "sales"
              ? editOrAddText + " pozycję danych sprzedażowych"
              : editOrAddText + " pozycję danych kosztowych"
          }}
        </span>
      </div>
    </template>
    <div class="flex flex-1 flex-col min-h-0 overflow-hidden card justify-center pt-2">
      <div class="card flex justify-center pt-2">
        <Form
          :initial-values="initialValues"
          :resolver="resolver"
          class="flex flex-col gap-4 w-full items-center sm:w-150"
          @submit="onFormSubmit"
        >
          <div class="flex gap-4 w-full">
            <!-- COLUMN 1 -->
            <div class="flex flex-col gap-4 w-full">
              <!-- Type select -->
              <FloatLabel variant="on">
                <Select
                  id="type_select"
                  v-model="selectedType"
                  :options="typeOptions"
                  class="h-10.5"
                  empty-message="Brak opcji do wyboru"
                  fluid
                >
                  <template #value="slotProps">
                    <div v-if="slotProps.value?.value" class="flex items-center gap-2">
                      <div v-tooltip.bottom="slotProps.value.description" class="flex flex-1">
                        {{ slotProps.value.label }}
                      </div>
                    </div>
                    <span v-else>
                      {{ slotProps.placeholder }}
                    </span>
                  </template>
                  <template #option="slotProps">
                    <div class="flex flex-1 items-center gap-2">
                      <div v-tooltip.bottom="slotProps.option.description" class="flex flex-1">
                        {{ slotProps.option.label }}
                      </div>
                    </div>
                  </template>
                  <template #dropdownicon>
                    <i class="pi pi-chevron-down" />
                  </template>
                </Select>
                <label for="type_select">Typ</label>
              </FloatLabel>
              <!-- name input -->
              <FormField v-slot="$field" name="name" class="flex flex-col gap-1">
                <FloatLabel variant="on">
                  <InputText v-bind="$field.props" id="name_input" type="text" fluid />
                  <label for="name_input">Nazwa pozycji/klienta/dostawcy</label>
                </FloatLabel>
                <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                  {{ $field.error?.message }}
                </Message>
              </FormField>
              <!-- netValue input -->
              <FormField v-slot="$field" name="netValue" class="flex flex-col gap-1">
                <FloatLabel variant="on">
                  <InputNumber
                    v-bind="$field.props"
                    id="netValue_input"
                    v-model="initialValues.netValue"
                    mode="currency"
                    currency="PLN"
                    locale="pl-PL"
                    fluid
                  />
                  <label for="netValue_input">Wartość netto</label>
                </FloatLabel>
                <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                  {{ $field.error?.message }}
                </Message>
              </FormField>
              <!-- paymentStatus select -->
              <FloatLabel variant="on">
                <Select
                  id="paymentStatus_select"
                  v-model="selectedPaymentStatus"
                  :options="paymentStatusOptions"
                  class="h-10.5"
                  empty-message="Brak opcji do wyboru"
                  fluid
                >
                  <template #value="slotProps">
                    <div v-if="slotProps.value" class="flex items-center gap-2">
                      <div v-tooltip.bottom="slotProps.value.label" class="flex flex-1">
                        {{ slotProps.value.label }}
                      </div>
                    </div>
                    <span v-else>
                      {{ slotProps.placeholder }}
                    </span>
                  </template>
                  <template #option="slotProps">
                    <div class="flex flex-1 items-center gap-2">
                      <div v-tooltip.bottom="slotProps.option.label" class="flex flex-1">
                        {{ slotProps.option.label }}
                      </div>
                    </div>
                  </template>
                  <template #dropdownicon>
                    <i class="pi pi-receipt" />
                  </template>
                </Select>
                <label for="paymentStatus_select">Status płatności</label>
              </FloatLabel>
            </div>

            <!-- COLUMN 2 -->
            <div class="flex flex-col gap-4 w-full">
              <!-- Date input -->
              <FloatLabel variant="on">
                <DatePicker
                  id="date_input"
                  v-model="selectedDate"
                  v-tooltip.bottom="
                    'Wybierz datę sprzedaży/zakupu, jeśli dane obejmują okres czasu, wybierz datę w miesiącu dla którego chcesz je przypisać'
                  "
                  date-format="dd/mm/yy"
                  placeholder="dd/mm/rrrr"
                  :manual-input="false"
                  show-button-bar
                  show-icon
                  icon-display="input"
                  :min-date="new Date(2000, 0, 1)"
                  :max-date="new Date(new Date().setFullYear(new Date().getFullYear() + 1))"
                  fluid
                >
                  <template #buttonbar="{ todayCallback }">
                    <Button
                      size="small"
                      severity="secondary"
                      variant="outlined"
                      @click="todayCallback"
                    >
                      Dziś
                    </Button>
                  </template>
                </DatePicker>
                <label for="date_input">Data</label>
              </FloatLabel>
              <!-- description input -->
              <FormField v-slot="$field" name="description" class="flex flex-col gap-1">
                <FloatLabel variant="on">
                  <InputText v-bind="$field.props" id="description_input" type="text" fluid />
                  <label for="description_input">Opis (Opcjonalnie)</label>
                </FloatLabel>
                <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
                  {{ $field.error?.message }}
                </Message>
              </FormField>
              <!-- taxRate select -->
              <FloatLabel variant="on">
                <Select
                  id="taxRate_select"
                  v-model="selectedTaxRate"
                  :options="props.taxRates"
                  class="h-10.5"
                  empty-message="Brak opcji do wyboru"
                  fluid
                >
                  <template #value="slotProps">
                    <div v-if="slotProps.value" class="flex items-center gap-2">
                      <div v-tooltip.bottom="slotProps.value.hint_text" class="flex flex-1">
                        {{ slotProps.value.display_text }}
                      </div>
                    </div>
                    <span v-else>
                      {{ slotProps.placeholder }}
                    </span>
                  </template>
                  <template #option="slotProps">
                    <div class="flex flex-1 items-center gap-2">
                      <div v-tooltip.bottom="slotProps.option.hint_text" class="flex flex-1">
                        {{ slotProps.option.display_text }}
                      </div>
                    </div>
                  </template>
                  <template #dropdownicon>
                    <i class="pi pi-money-bill" />
                  </template>
                </Select>
                <label for="taxRate_select">Stawka VAT</label>
              </FloatLabel>
            </div>
          </div>
          <Button
            type="submit"
            severity="secondary"
            label="Dodaj wiersz"
            :loading="props.loading || submitDisabled"
            :disabled="props.loading || submitDisabled"
            class="sm:w-100"
          />
        </Form>
      </div>
    </div>
  </Dialog>
</template>
