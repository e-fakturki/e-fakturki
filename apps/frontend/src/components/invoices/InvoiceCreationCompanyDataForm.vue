<script setup lang="ts">
import { Form, FormField } from "@primevue/forms";
import { Panel, InputText, FloatLabel, Message, Select, useToast } from "primevue";
import { ref, watch } from "vue";
import { useCurrentUserStore } from "../../stores/currentUserStore";
import type { IsoCountries } from "../../lib/types/company";
import { useMutation } from "@tanstack/vue-query";
import { getIsoCountries } from "../../lib/services/companyService";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import z from "zod";
import { emptyToNull } from "../../lib/utils";

const props = defineProps<{
  seller: boolean;
  disabled: boolean;
}>();
const emit = defineEmits<{
  update: [
    {
      name: string;
      nip: string;
      krs: string | null;
      regon: string | null;
      countryCode: string;
      addressL1: string;
      addressL2: string | null;
      addressCorrespondanceL1: string | null;
      addressCorrespondanceL2: string | null;
      email: string | null;
      phoneNumber: string | null;
    },
  ];
}>();
const toast = useToast();
const currentUserStore = useCurrentUserStore();
const countries = ref<IsoCountries[]>([]);

const resolver = zodResolver(
  z.object({
    name: z
      .string()
      .min(3, { message: "Nazwa musi mieć min. 3 znaki." })
      .max(256, { message: "Nazwa firmy może mieć maksymalnie 256 znaków." }),
    nip: z
      .string()
      .min(1, { message: "NIP jest wymagany." })
      .max(10, { message: "NIP może zawierać maksymalnie 10 cyfr." })
      .refine((val) => /^[1-9]((\d[1-9])|([1-9]\d))\d{7}$/.test(val), {
        message: "NIP musi być poprawny.",
      }),
    krs: z
      .string()
      .refine((val) => val === "" || /^\d{10}$/.test(val), {
        message: "KRS musi mieć dokładnie 10 cyfr lub pozostać pusty",
      })
      .nullable(),
    regon: z
      .string()
      .refine((val) => val === "" || /^(\d{14})$/.test(val), {
        message: "REGON musi mieć 14 cyfr lub pozostać pusty",
      })
      .nullable(),
    countryCode: z.string().min(2, { message: "Kraj jest wymagany." }),
    addressL1: z
      .string()
      .min(3, { message: "Pierwsza linia adresu musi mieć min. 3 znaki." })
      .max(512, { message: "Adres przekracza maksymalny rozmiar." }),
    addressL2: z.string().max(512, { message: "Adres przekracza maksymalny rozmiar." }).nullable(),
    email: z
      .string()
      .refine(
        (val) =>
          val === "" ||
          /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/.test(
            val,
          ),
        {
          message: "Wpisz poprawny e-mail lub pozostaw puste pole.",
        },
      )
      .nullable(),
    phoneNumber: z
      .string()
      .max(16, {
        message: "Numer telefonu może zawierać maksymalnie 16 znaków. (Wpisuj bez spacji)",
      })
      .nullable(),
    addressCorrespondanceL1: z
      .string()
      .max(512, {
        message: "Adres przekracza maksymalny rozmiar.",
      })
      .nullable(),
    addressCorrespondanceL2: z
      .string()
      .max(512, {
        message: "Adres przekracza maksymalny rozmiar.",
      })
      .nullable(),
  }),
);

const getCountryCodesMutation = useMutation({
  mutationFn: async () => {
    return await getIsoCountries();
  },

  onSuccess: (data) => {
    countries.value = data;
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

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
}

defineExpose({
  validate,
  reset,
});

// initialization watch
watch(
  () => props.seller,
  async () => {
    await getCountryCodesMutation.mutateAsync();
    if (props.seller) {
      formRef.value.states.countryCode.value = countries.value.find(
        (c) => c.value === currentUserStore.getCompanyCountryCode,
      )?.value;
    } else {
      formRef.value.states.countryCode.value = countries.value.find((c) => c.value === "PL")?.value;
    }
  },
  { immediate: true },
);

watch(
  // A watcher that emits the updated values with every change to the form values
  () => formRef.value?.states,
  (values) => {
    emit("update", {
      name: values.name.value,
      nip: values.nip.value,
      krs: emptyToNull(values.krs.value),
      regon: emptyToNull(values.regon.value),
      countryCode: values.countryCode.value,
      addressL1: emptyToNull(values.addressL1.value),
      addressL2: emptyToNull(values.addressL2.value),
      addressCorrespondanceL1: emptyToNull(values.addressCorrespondanceL1.value),
      addressCorrespondanceL2: emptyToNull(values.addressCorrespondanceL2.value),
      email: emptyToNull(values.email.value),
      phoneNumber: emptyToNull(values.phoneNumber.value),
    });
  },
  { deep: true },
);
</script>

<template>
  <Panel>
    <template #header>
      <span class="text-xl font-bold">
        {{ props.seller ? "Dane sprzedawcy" : "Dane nabywcy" }}
      </span>
    </template>

    <Form ref="formRef" :resolver="resolver" class="flex flex-col gap-2 w-full sm:w-100 pb-2">
      <!-- COMPANY NAME -->
      <FormField
        v-slot="$field"
        :initialValue="props.seller ? currentUserStore.getCompanyName : ''"
        name="name"
        class="flex flex-col gap-1"
        v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
      >
        <FloatLabel variant="on">
          <InputText
            :readonly="props.seller"
            v-bind="$field.props"
            v-model="$field.value"
            :disabled="props.disabled"
            id="company_name_input"
            type="text"
            fluid
          />
          <label for="company_name_input">Nazwa firmy</label>
        </FloatLabel>

        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
          {{ $field.error?.message }}
        </Message>
      </FormField>

      <!-- NIP -->
      <FormField
        v-slot="$field"
        name="nip"
        :initialValue="props.seller ? currentUserStore.getCompanyNip : ''"
        class="flex flex-col gap-1"
        v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
      >
        <FloatLabel variant="on">
          <InputText
            :readonly="props.seller"
            v-bind="$field.props"
            v-model="$field.value"
            :disabled="props.disabled"
            id="company_nip_input"
            type="text"
            fluid
          />
          <label for="company_nip_input">NIP firmy</label>
        </FloatLabel>

        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
          {{ $field.error?.message }}
        </Message>
      </FormField>

      <!-- KRS -->
      <FormField
        v-slot="$field"
        name="krs"
        :initialValue="props.seller ? currentUserStore.getCompanyKrs : ''"
        class="flex flex-col gap-1"
        v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
      >
        <FloatLabel variant="on">
          <InputText
            :readonly="props.seller"
            v-bind="$field.props"
            v-model="$field.value"
            :disabled="props.disabled"
            id="company_krs_input"
            type="text"
            fluid
          />
          <label for="company_krs_input"> KRS firmy (Opcjonalnie) </label>
        </FloatLabel>

        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
          {{ $field.error?.message }}
        </Message>
      </FormField>

      <!-- REGON -->
      <FormField
        v-slot="$field"
        name="regon"
        :initialValue="props.seller ? currentUserStore.getCompanyRegon : ''"
        class="flex flex-col gap-1"
        v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
      >
        <FloatLabel variant="on">
          <InputText
            :readonly="props.seller"
            v-bind="$field.props"
            v-model="$field.value"
            :disabled="props.disabled"
            id="company_regon_input"
            type="text"
            fluid
          />
          <label for="company_regon_input"> REGON firmy (Opcjonalnie) </label>
        </FloatLabel>

        <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
          {{ $field.error?.message }}
        </Message>
      </FormField>

      <!-- ADDRESS -->
      <Panel :header="props.seller ? 'Adres sprzedawcy' : 'Adres nabywcy'" toggleable collapsed>
        <div class="flex flex-col gap-2">
          <!-- COUNTRY -->
          <FormField
            v-slot="$field"
            name="countryCode"
            :initialValue="props.seller ? currentUserStore.getCompanyCountryCode : 'PL'"
            v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
          >
            <Select
              v-bind="$field.props"
              :options="countries"
              :disabled="props.seller || props.disabled"
              optionLabel="label"
              optionValue="value"
              placeholder="Kraj"
              fluid
            >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center gap-2">
                  <img
                    :alt="slotProps.value.label"
                    :src="`https://flagcdn.com/${slotProps.value?.toLowerCase()}.svg`"
                    style="width: 24px"
                    loading="lazy"
                  />

                  <div>{{ countries.find((c) => c.value === slotProps.value)?.label }}</div>
                </div>

                <span v-else>
                  {{ slotProps.placeholder }}
                </span>
              </template>

              <template #option="slotProps">
                <div class="flex items-center gap-2">
                  <img
                    :alt="slotProps.option.label"
                    :src="`https://flagcdn.com/${slotProps.option.value?.toLowerCase()}.svg`"
                    style="width: 24px"
                    loading="lazy"
                  />

                  <div>{{ slotProps.option.label }}</div>
                </div>
              </template>

              <template #dropdownicon>
                <i class="pi pi-map" />
              </template>
            </Select>
          </FormField>

          <!-- ADDRESS LINE 1 -->
          <FormField
            v-slot="$field"
            :initialValue="props.seller ? currentUserStore.getCompanyAddressL1 : ''"
            name="addressL1"
            class="flex flex-col gap-1"
            v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
          >
            <FloatLabel variant="on">
              <InputText
                :readonly="props.seller"
                v-bind="$field.props"
                v-model="$field.value"
                :disabled="props.disabled"
                id="address_l1_input"
                type="text"
                fluid
              />
              <label for="address_l1_input"> Adres linia 1 (Opcjonalnie) </label>
            </FloatLabel>

            <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
              {{ $field.error?.message }}
            </Message>
          </FormField>

          <!-- ADDRESS LINE 2 -->
          <FormField
            v-slot="$field"
            :initialValue="props.seller ? currentUserStore.getCompanyAddressL2 : ''"
            name="addressL2"
            class="flex flex-col gap-1"
            v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
          >
            <FloatLabel variant="on">
              <InputText
                :readonly="props.seller"
                v-bind="$field.props"
                v-model="$field.value"
                :disabled="props.disabled"
                id="address_l2_input"
                type="text"
                fluid
              />
              <label for="address_l2_input"> Adres linia 2 (Opcjonalnie) </label>
            </FloatLabel>

            <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
              {{ $field.error?.message }}
            </Message>
          </FormField>
        </div>
      </Panel>

      <!-- CONTACT -->
      <Panel :header="props.seller ? 'Kontakt sprzedawcy' : 'Kontakt nabywcy'" toggleable collapsed>
        <div class="flex flex-col gap-2">
          <!-- EMAIL -->
          <FormField
            v-slot="$field"
            :initialValue="props.seller ? currentUserStore.getCompanyEmail : ''"
            name="email"
            class="flex flex-col gap-1"
            v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
          >
            <FloatLabel variant="on">
              <InputText
                :readonly="props.seller"
                v-bind="$field.props"
                v-model="$field.value"
                :disabled="props.disabled"
                id="company_email_input"
                type="text"
                fluid
              />
              <label for="company_email_input"> E-mail (Opcjonalnie) </label>
            </FloatLabel>
            <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
              {{ $field.error?.message }}
            </Message>
          </FormField>

          <!-- PHONE -->
          <FormField
            v-slot="$field"
            :initialValue="props.seller ? currentUserStore.getCompanyPhoneNumber : ''"
            name="phoneNumber"
            class="flex flex-col gap-1"
            v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
          >
            <FloatLabel variant="on">
              <InputText
                :readonly="props.seller"
                v-bind="$field.props"
                v-model="$field.value"
                :disabled="props.disabled"
                id="company_phone_input"
                type="text"
                fluid
              />
              <label for="company_phone_input"> Telefon (Opcjonalnie) </label>
            </FloatLabel>
            <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
              {{ $field.error?.message }}
            </Message>
          </FormField>

          <!-- ADDRESS CORRESPONDANCE LINE 2 -->
          <FormField
            v-slot="$field"
            :initialValue="props.seller ? currentUserStore.getCompanyAddressCorrespondanceL1 : ''"
            name="addressCorrespondanceL1"
            class="flex flex-col gap-1"
            v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
          >
            <FloatLabel variant="on">
              <InputText
                :readonly="props.seller"
                v-bind="$field.props"
                v-model="$field.value"
                :disabled="props.disabled"
                id="correspondence_address_l1_input"
                type="text"
                fluid
              />
              <label for="correspondence_address_l1_input">
                Adres korespondencyjny linia 1 (Opcjonalnie)
              </label>
            </FloatLabel>
            <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
              {{ $field.error?.message }}
            </Message>
          </FormField>

          <!-- ADDRESS CORRESPONDANCE LINE 2 -->
          <FormField
            v-slot="$field"
            :initialValue="props.seller ? currentUserStore.getCompanyAddressCorrespondanceL2 : ''"
            name="addressCorrespondanceL2"
            class="flex flex-col gap-1"
            v-tooltip.top="props.seller ? 'Dane własnej firmy można zmienić w zakładce Firmy' : ''"
          >
            <FloatLabel variant="on">
              <InputText
                :readonly="props.seller"
                v-bind="$field.props"
                v-model="$field.value"
                :disabled="props.disabled"
                id="correspondence_address_l2_input"
                type="text"
                fluid
              />
              <label for="correspondence_address_l2_input">
                Adres korespondencyjny linia 2 (Opcjonalnie)
              </label>
            </FloatLabel>

            <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">
              {{ $field.error?.message }}
            </Message>
          </FormField>
        </div>
      </Panel>
    </Form>
  </Panel>
</template>
