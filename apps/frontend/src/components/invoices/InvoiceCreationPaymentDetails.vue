<script setup lang="ts">
import { Form, FormField } from "@primevue/forms";
import { Panel, InputText, FloatLabel, Message, DatePicker, Select, Tag } from "primevue";
import { ref, watch } from "vue";
import {
  paymentStatusMapForComponents,
  paymentStatusSeverity,
  paymentTypeMapForComponents,
} from "../../lib/types/invoices";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import z from "zod";
import { emptyToNull } from "../../lib/utils";

const props = defineProps<{
  disabled: boolean;
}>();
const emit = defineEmits<{
  update: [
    {
      paymentStatus: string;
      paymentType: number;
      iban?: string | null;
      bankName?: string | null;
      paymentDueDate: Date | null;
      paymentDate: Date | null;
    },
  ];
  completed: [];
}>();
const paid = ref<boolean>(false);
const cash = ref<boolean>(true);

const resolver = zodResolver(
  z
    .object({
      paymentStatus: z.string().min(1, { message: "Status płatności jest wymagany." }),
      paymentType: z.number().int().min(1, { message: "Rodzaj płatności jest wymagany." }),
      iban: z
        .string()
        .max(34, { message: "Numer konta musi mieć maksymalnie 34 znaki." })
        .optional(),
      bankName: z
        .string()
        .max(256, { message: "Nazwa Banku musi mieć maksymalnie 256 znaków." })
        .optional(),
      paymentDueDate: z.date().nullable(),
      paymentDate: z.date().nullable(),
    })
    .refine((data) => data.paymentDueDate !== null || data.paymentDate !== null, {
      message: "Należy podać termin płatności lub datę płatności.",
      path: ["paymentDueDate"],
    })
    .refine(
      (data) => {
        if (data.paymentType === 1) return true;

        return !!data.iban && !!data.bankName;
      },
      {
        message: "Należy podać numer konta bankowego i nazwę banku.",
        path: ["iban"],
      },
    ),
);

function onSelectPaymentStatus(event: any) {
  if (event.value === "paid") {
    formRef.value.states.paymentStatus.value = "paid";
    formRef.value.states.paymentDueDate.value = null;
    paid.value = true;
  }

  if (event.value === "unpaid") {
    formRef.value.states.paymentStatus.value = "unpaid";
    formRef.value.states.paymentDate.value = null;
    paid.value = false;
  }
}

function onSelectPaymentType(event: any) {
  if (event.value === 1) {
    formRef.value.states.paymentType.value = 1;
    formRef.value.states.iban.value = "";
    formRef.value.states.bankName.value = "";
    cash.value = true;
  } else {
    formRef.value.states.paymentType.value = event.value;
    cash.value = false;
  }
}

// reference to the form to expose the validaiton and submit
// for the parent component
const formRef = ref();

async function validate() {
  const result = await formRef.value?.validate();
  const isValid = !result?.errors || Object.keys(result.errors).length === 0;
  return isValid;
}

function reset() {
  formRef.value.reset();
  paid.value = false;
  cash.value = true;
}

defineExpose({
  validate,
  reset,
});

watch(
  // A watcher that emits the updated values with every change to the form values
  () => formRef.value?.states,
  (values) => {
    emit("update", {
      paymentStatus: values.paymentStatus.value,
      paymentType: values.paymentType.value,
      iban: values.iban ? emptyToNull(values.iban.value) : "",
      bankName: values.bankName ? emptyToNull(values.bankName.value) : "",
      paymentDueDate: values.paymentDueDate.value,
      paymentDate: values.paymentDate.value,
    });
  },
  { deep: true },
);
</script>

<template>
  <Panel>
    <template #header>
      <span class="text-xl font-bold">Płatność</span>
    </template>
    <Form ref="formRef" :resolver="resolver" class="flex flex-col gap-2 w-full sm:w-100 pb-2">
      <!-- PAYMENT STATUS -->
      <FormField
        v-slot="$field"
        initialValue="unpaid"
        name="paymentStatus"
        class="flex flex-col gap-1"
      >
        <FloatLabel variant="on">
          <Select
            v-bind="$field.props"
            :options="paymentStatusMapForComponents"
            optionLabel="label"
            optionValue="value"
            :disabled="props.disabled"
            :optionDisabled="(option) => option.value === 'partial'"
            @change="onSelectPaymentStatus"
            fluid
          >
            <template #option="slotProps">
              <Tag
                :value="slotProps.option.label"
                :severity="paymentStatusSeverity[slotProps.option.value]"
              />
            </template>

            <template #value="slotProps">
              <Tag
                v-if="slotProps.value"
                :value="
                  paymentStatusMapForComponents.find((o) => o.value === slotProps.value)?.label
                "
                :severity="paymentStatusSeverity[slotProps.value]"
              />
            </template>
          </Select>
          <label for="name_input">Status płatności</label>
        </FloatLabel>
        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
          $field.error?.message
        }}</Message>

        <!-- PAYMENT TYPE -->
      </FormField>
      <FormField v-slot="$field" :initialValue="1" name="paymentType" class="flex flex-col gap-1">
        <FloatLabel variant="on">
          <Select
            v-bind="$field.props"
            :options="paymentTypeMapForComponents"
            :disabled="props.disabled"
            @change="onSelectPaymentType"
            optionLabel="label"
            optionValue="value"
            fluid
          >
          </Select>
          <label for="name_input">Rodzaj płatności</label>
        </FloatLabel>
        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
          $field.error?.message
        }}</Message>
      </FormField>

      <!-- BANK DETAILS -->
      <Panel v-if="!cash" header="Dane płatności" toggleable collapsed>
        <div class="flex flex-col gap-2">
          <!-- IBAN -->
          <FormField v-slot="$field" initialValue="" name="iban" class="flex flex-col gap-1">
            <FloatLabel variant="on">
              <InputText
                v-bind="$field.props"
                v-model="$field.value"
                :disabled="props.disabled"
                id="iban_input"
                type="text"
                fluid
              />
              <label for="iban_input">Numer rachunku bankowego (IBAN)</label>
            </FloatLabel>
            <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
              $field.error?.message
            }}</Message>
          </FormField>

          <!-- BANK NAME -->
          <FormField v-slot="$field" initialValue="" name="bankName" class="flex flex-col gap-1">
            <FloatLabel variant="on">
              <InputText
                v-bind="$field.props"
                v-model="$field.value"
                :disabled="props.disabled"
                id="bankName_input"
                type="text"
                fluid
              />
              <label for="bankName_input">Nazwa Banku</label>
            </FloatLabel>
            <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
              $field.error?.message
            }}</Message>
          </FormField>
        </div>
      </Panel>

      <!-- PAYMENT DUE DATE -->
      <FormField
        v-slot="$field"
        :initialValue="null"
        name="paymentDueDate"
        class="flex flex-col gap-1"
      >
        <FloatLabel variant="on">
          <DatePicker
            v-bind="$field.props"
            v-model="$field.value"
            :disabled="paid || props.disabled"
            inputId="payDueDate"
            dateFormat="yy/mm/dd"
            fluid
            showIcon
            iconDisplay="input"
          />
          <label for="payDueDate">Termin płatności</label>
        </FloatLabel>
        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
          {{ $field.error?.message }}
        </Message>
      </FormField>

      <!-- PAYMENT DATE -->
      <FormField
        v-slot="$field"
        :initialValue="null"
        name="paymentDate"
        class="flex flex-col gap-1"
      >
        <FloatLabel variant="on">
          <DatePicker
            v-bind="$field.props"
            v-model="$field.value"
            :disabled="!paid || props.disabled"
            inputId="payDate"
            dateFormat="yy/mm/dd"
            fluid
            showIcon
            iconDisplay="input"
          />
          <label for="payDate">Data płatności</label>
        </FloatLabel>
        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
          $field.error?.message
        }}</Message>
      </FormField>
    </Form>
  </Panel>
</template>
