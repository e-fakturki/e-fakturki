<script setup lang="ts">
import { Form, FormField } from "@primevue/forms";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import { Panel, InputText, FloatLabel, Message, DatePicker } from "primevue";
import { watch, ref } from "vue";
import z from "zod";

const props = defineProps<{
  disabled: boolean;
}>();

const emit = defineEmits<{
  update: [
    {
      invoiceNumber: string;
      issuePlace: string;
      invoiceDate: Date | null;
    },
  ];
}>();

const resolver = zodResolver(
  z.object({
    invoiceNumber: z
      .string()
      .min(1, { message: "Numer faktury jest wymagany." })
      .max(256, { message: "Numer faktury może mieć maksymalnie 256 znaków." }),
    invoiceDate: z.date(),
    issuePlace: z.string().min(1, { message: "Miejsce wystawienia jest wymagane." }).max(256, {
      message: "Miejsce wystawienia może mieć maksymalnie 256 znaków.",
    }),
  }),
);

// reference to the form
const formRef = ref();
const initialInvoiceDate = new Date();

async function validate() {
  const result = await formRef.value?.validate();
  const isValid = !result?.errors || Object.keys(result.errors).length === 0;
  return isValid;
}

function reset() {
  formRef.value.reset();
}

defineExpose({
  validate,
  reset,
});

watch(
  // A watcher that emits the updated values with every change to the form values
  () => formRef.value?.states,
  (values) => {
    if (!values) return;

    emit("update", {
      invoiceNumber: values.invoiceNumber.value,
      issuePlace: values.issuePlace.value,
      invoiceDate: values.invoiceDate.value,
    });
  },
  { deep: true },
);
</script>

<template>
  <Panel class="flex flex-1">
    <template #header>
      <span class="text-xl font-bold">Dane Faktury</span>
    </template>

    <Form ref="formRef" :resolver="resolver" class="flex flex-1 gap-4">
      <!-- INVOICE NUMBER -->
      <FormField v-slot="$field" initialValue="" name="invoiceNumber" class="sm:w-100">
        <FloatLabel variant="on">
          <InputText
            v-bind="$field.props"
            v-model="$field.value"
            :disabled="props.disabled"
            id="invoiceNumber_input"
            type="text"
            fluid
          />
          <label for="invoiceNumber_input">Numer Faktury</label>
        </FloatLabel>
        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
          {{ $field.error?.message }}
        </Message>
      </FormField>

      <!-- INVOICE DATE -->
      <FormField
        v-slot="$field"
        :initialValue="initialInvoiceDate"
        name="invoiceDate"
        class="sm:w-100"
      >
        <FloatLabel variant="on">
          <DatePicker
            v-bind="$field.props"
            v-model="$field.value"
            :disabled="props.disabled"
            inputId="invoiceDate"
            dateFormat="yy/mm/dd"
            fluid
            showIcon
            iconDisplay="input"
          />
          <label for="invoiceDate">Data wystawienia</label>
        </FloatLabel>
      </FormField>

      <!-- ISSUE PLACE -->
      <FormField v-slot="$field" initialValue="" name="issuePlace" class="sm:w-100">
        <FloatLabel variant="on">
          <InputText
            v-bind="$field.props"
            v-model="$field.value"
            :disabled="props.disabled"
            id="issuePlace_input"
            type="text"
            fluid
          />
          <label for="issuePlace_input">Miejsce wystawienia</label>
        </FloatLabel>

        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
          {{ $field.error?.message }}
        </Message>
      </FormField>
    </Form>
  </Panel>
</template>
