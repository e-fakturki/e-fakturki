<script setup lang="ts">
import { useToast } from "primevue";
import { Message, FloatLabel, InputText, Dialog, Button, Select, InputNumber } from "primevue";
import { Form, FormField, type FormSubmitEvent } from "@primevue/forms";

import { useCurrentUserStore } from "../../stores/currentUserStore";
import { reactive, ref, watch } from "vue";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import { useMutation } from "@tanstack/vue-query";
import z from "zod";
import type { CreateOrUpdate } from "../../lib/types/company";
import type { ProductListItem, TaxRate } from "../../lib/types/products";
import { createProduct, updateProduct } from "../../lib/services/productService";
import { calculateGrossPrice, calculateNetPrice, verifyNetVsGrossPrice } from "../../lib/utils";

const props = withDefaults(
  defineProps<{
    visible: boolean;
    createOrUpdate: CreateOrUpdate;
    productInfo: ProductListItem | null;
    taxRates: TaxRate[];
    loading?: boolean;
  }>(),
  {
    productInfo: null,
  },
);
const emit = defineEmits(["update:visible", "success", "cancel"]);
const toast = useToast();
const currentUserStore = useCurrentUserStore();
const selectedTaxRate = ref<TaxRate | null>(null);

const initialValues = reactive({
  name: "",
  description: "",
  gtin: "",
  unit: "",
  netPrice: 0,
  grossPrice: 0,
});

function resetInitialValues() {
  initialValues.name = props.productInfo?.name ?? "";
  initialValues.description = props.productInfo?.description ?? "";
  initialValues.gtin = props.productInfo?.gtin ?? "";
  initialValues.unit = props.productInfo?.unit ?? "";
  initialValues.netPrice = props.productInfo?.net_price ?? 0;
  initialValues.grossPrice = props.productInfo?.gross_price ?? 0;
}

const resolver = zodResolver(
  z.object({
    name: z.string().min(1, { message: "Nazwa produktu jest wymagana." }),
    description: z.string().max(2048, { message: "Opis przekracza maksymalny rozmiar." }),
    gtin: z.string().max(20, { message: "GTIN może zawierać maksymalnie 20 cyfr." }),
    unit: z
      .string()
      .max(256, { message: "Jednostka miary przekracza maksymalny rozmiar." })
      .min(1, { message: "Jednostka miary jest wymagana." }),
    netPrice: z
      .number({ message: "Cena netto musi być liczbą." })
      .min(0, { message: "Cena netto musi być nieujemna." }),
    grossPrice: z.coerce
      .number({ message: "Cena brutto musi być liczbą." })
      .min(0, { message: "Cena brutto musi być nieujemna." }),
  }),
);

const createProductMutation = useMutation({
  mutationFn: async (values: any) => {
    const productResp = await createProduct({
      name: values.name,
      company_id: currentUserStore.getCompanyId,
      description: values.description,
      gtin: values.gtin,
      unit: values.unit,
      net_price: values.netPrice,
      tax_rate: selectedTaxRate.value?.str_repr,
      gross_price: values.grossPrice,
    });

    return productResp;
  },

  onSuccess: () => {
    toast.add({ severity: "success", summary: "Produkt dodany pomyślnie!", life: 3000 });
    emit("success");
  },

  onError: (error) => {
    console.log(error);
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

const updateProductMutation = useMutation({
  mutationFn: async (values: any) => {
    const productResp = await updateProduct({
      id: props.productInfo?.id,
      name: values.name,
      company_id: currentUserStore.getCompanyId,
      description: values.description,
      gtin: values.gtin,
      unit: values.unit,
      net_price: values.netPrice,
      tax_rate: selectedTaxRate.value?.str_repr,
      gross_price: values.grossPrice,
    });

    return productResp;
  },

  onSuccess: () => {
    toast.add({
      severity: "success",
      summary: "Produkt zaaktualizowany pomyślnie!",
      life: 3000,
    });
    emit("success");
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

const onFormSubmit = async (event: FormSubmitEvent) => {
  const { valid } = event;
  if (!valid) return;

  const values = {
    ...event.values,
    grossPrice: calculateGrossPrice(event.values.netPrice, selectedTaxRate.value!.value),
  };

  if (verifyNetVsGrossPrice(values.netPrice, values.grossPrice, selectedTaxRate.value?.value)) {
    if (props.createOrUpdate === "update") updateProductMutation.mutate(values);
    if (props.createOrUpdate === "create") createProductMutation.mutate(values);
  } else throw new Error("Ceny netto i brutto nie zgadzają się.");
};

function onNetPriceChange(event: any) {
  initialValues.netPrice = event.value;

  if (initialValues.netPrice == null || !selectedTaxRate.value) {
    return;
  }

  initialValues.grossPrice = calculateGrossPrice(
    initialValues.netPrice,
    selectedTaxRate.value.value,
  );
}

function onTaxRateChange() {
  if (initialValues.netPrice == null || !selectedTaxRate.value) {
    return;
  }

  initialValues.grossPrice = calculateGrossPrice(
    initialValues.netPrice,
    selectedTaxRate.value.value,
  );
}

watch(
  () => props.visible,
  async (visible) => {
    if (visible) {
      resetInitialValues();
      if (props.createOrUpdate === "update") {
        selectedTaxRate.value = props.taxRates.find(
          (tax) => tax.str_repr === props.productInfo?.tax_rate,
        );
      } else {
        selectedTaxRate.value = props.taxRates.find((c) => c.str_repr === "23");
      }
    }
  },
);
</script>

<template>
  <Dialog
    :visible="visible"
    @update:visible="emit('update:visible', $event)"
    modal
    :draggable="false"
    :style="{ width: '40rem' }"
  >
    <template #header>
      <div v-if="props.createOrUpdate === 'update'" class="flex flex-col text-xl font-semibold">
        <span> Edytuj dane produktu firmy: </span>
        <span>{{ currentUserStore.getCompanyName }}</span>
      </div>
      <div v-if="props.createOrUpdate === 'create'" class="flex flex-col text-xl font-semibold">
        <span> Dodaj nowy produkt dla firmy: </span>
        <span>{{ currentUserStore.getCompanyName }}</span>
      </div>
    </template>
    <div class="card flex justify-center pt-2">
      <Form
        :initialValues="initialValues"
        v-slot="$form"
        :resolver="resolver"
        @submit="onFormSubmit"
        class="flex flex-col gap-4 w-full items-center sm:w-150"
      >
        <div class="flex gap-4 w-full">
          <div class="flex flex-col gap-4 w-full">
            <FormField v-slot="$field" name="name" class="flex flex-col gap-1">
              <FloatLabel variant="on">
                <InputText v-bind="$field.props" id="name_input" type="text" fluid />
                <label for="name_input">Nazwa produktu</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField v-slot="$field" name="gtin" class="flex flex-col gap-1">
              <FloatLabel variant="on">
                <InputText v-bind="$field.props" id="gtin_input" type="text" fluid />
                <label for="gtin_input">GTIN (Opcjonalnie)</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField v-slot="$field" name="description" class="flex flex-col gap-1">
              <FloatLabel variant="on">
                <InputText v-bind="$field.props" id="description_input" type="text" fluid />
                <label for="description_input">Opis produktu (Opcjonalnie)</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField v-slot="$field" name="unit" class="flex flex-col gap-1">
              <FloatLabel variant="on">
                <InputText v-bind="$field.props" id="unit_input" type="text" fluid />
                <label for="unit_input">Jednostka miary</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
          </div>
          <div class="flex flex-col gap-4 w-full">
            <FormField v-slot="$field" name="netPrice" class="flex flex-col gap-1">
              <FloatLabel variant="on">
                <InputNumber
                  v-bind="$field.props"
                  v-model="initialValues.netPrice"
                  id="netPrice_input"
                  mode="currency"
                  currency="PLN"
                  locale="pl-PL"
                  fluid
                  @input="onNetPriceChange"
                />
                <label for="netPrice_input">Cena netto</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FloatLabel variant="on">
              <Select
                v-model="selectedTaxRate"
                id="taxRate_select"
                :options="taxRates"
                class="h-10.5"
                emptyMessage="Brak opcji do wyboru"
                fluid
                @change="onTaxRateChange"
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
            <FormField v-slot="$field" name="grossPrice" class="flex flex-col gap-1">
              <FloatLabel variant="on">
                <InputNumber
                  v-bind="$field.props"
                  v-model="initialValues.grossPrice"
                  id="grossPrice_input"
                  mode="currency"
                  currency="PLN"
                  locale="pl-PL"
                  fluid
                  disabled
                />
                <label for="grossPrice_input">Cena brutto</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
          </div>
        </div>
        <Button
          type="submit"
          severity="secondary"
          :label="props.createOrUpdate === 'update' ? 'Zmień dane produktu' : 'Dodaj produkt'"
          :loading="updateProductMutation.isPending.value || createProductMutation.isPending.value"
          :disabled="updateProductMutation.isPending.value || createProductMutation.isPending.value"
          class="sm:w-100"
        />
      </Form>
    </div>
  </Dialog>
</template>
