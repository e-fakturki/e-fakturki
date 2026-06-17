<script setup lang="ts">
import { useToast } from "primevue";
import { Message, FloatLabel, InputText, Dialog, Button, Select } from "primevue";
import { Form, FormField, type FormSubmitEvent } from "@primevue/forms";

import { useCurrentUserStore } from "../../stores/currentUserStore";
import { computed, ref, watch } from "vue";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import { useMutation } from "@tanstack/vue-query";
import {
  updateCompany,
  getIsoCountries,
  createCompany,
  getUserCompany,
} from "../../lib/services/companyService";
import z from "zod";
import type { CompanyReadUpdate, CreateOrUpdate, IsoCountries } from "../../lib/types/company";
import { emptyToNull } from "../../lib/utils";

const props = withDefaults(
  defineProps<{
    visible: boolean;
    createOrUpdate: CreateOrUpdate;
    userCompany: boolean;
    companyInfo: CompanyReadUpdate | null;
    loading?: boolean;
  }>(),
  {
    companyInfo: null,
  },
);
const emit = defineEmits(["update:visible", "success", "cancel"]);
const toast = useToast();
const currentUserStore = useCurrentUserStore();
const countries = ref<IsoCountries[]>([]);
const dialogClosable = !(props.userCompany && props.createOrUpdate === "create");
const formRef = ref();

const resolver = zodResolver(
  z.object({
    name: z
      .string()
      .min(1, { message: "Nazwa firmy jest wymagana." })
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
    addressL1: z.string().max(512, { message: "Adres przekracza maksymalny rozmiar." }).nullable(),
    addressL2: z.string().max(512, { message: "Adres przekracza maksymalny rozmiar." }).nullable(),
    addressCorrespondanceL1: z
      .string()
      .max(512, { message: "Adres przekracza maksymalny rozmiar." })
      .nullable(),
    addressCorrespondanceL2: z
      .string()
      .max(512, { message: "Adres przekracza maksymalny rozmiar." })
      .nullable(),
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
    additionalInfo: z
      .string()
      .max(2048, { message: "Informacja dodatkowa przekracza maksymalny rozmiar." })
      .nullable(),
  }),
);

const createCompanyMutation = useMutation({
  mutationFn: async (values: any) => {
    const companyResp = await createCompany({
      owner_id: props.userCompany ? currentUserStore.getUserId : null,
      name: values.name,
      nip: values.nip,
      krs: emptyToNull(values.krs),
      regon: emptyToNull(values.regon),
      country_code: values.countryCode,
      address_l1: emptyToNull(values.addressL1),
      address_l2: emptyToNull(values.addressL2),
      address_correspondance_l1: emptyToNull(values.addressCorrespondanceL1),
      address_correspondance_l2: emptyToNull(values.addressCorrespondanceL2),
      email: emptyToNull(values.email),
      phone_number: emptyToNull(values.phoneNumber),
      additional_info: emptyToNull(values.additionalInfo),
    });

    return companyResp;
  },

  onSuccess: (data) => {
    if (props.userCompany && props.createOrUpdate === "create") {
      currentUserStore.setCompanyData({
        id: data.id,
        owner_id: data.owner_id,
        ksef_authorized: false,
        name: formRef.value.states.name.value,
        nip: formRef.value.states.nip.value,
        krs: formRef.value.states.krs.value ?? null,
        regon: formRef.value.states.regon.value ?? null,
        country_code: formRef.value.states.countryCode.value,
        address_l1: formRef.value.states.addressL1.value ?? null,
        address_l2: formRef.value.states.addressL2.value ?? null,
        address_correspondance_l1: formRef.value.states.addressCorrespondanceL1.value ?? null,
        address_correspondance_l2: formRef.value.states.addressCorrespondanceL2.value ?? null,
        email: formRef.value.states.email.value ?? null,
        phone_number: formRef.value.states.phoneNumber.value ?? null,
        additional_info: formRef.value.states.additionalInfo.value ?? null,
      });
    }
    toast.add({ severity: "success", summary: "Firma dodana pomyślnie!", life: 3000 });
    emit("success");
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

const getCompanyMutation = useMutation({
  mutationFn: async () => {
    return await getUserCompany();
  },
  onSuccess: (data) => {
    toast.add({ severity: "info", summary: "Poprawnie załadowano dane firmy", life: 3000 });
    currentUserStore.setCompanyData({
      id: data.id,
      owner_id: data.owner_id,
      ksef_authorized: data.ksef_authorized,
      name: data.name,
      nip: data.nip,
      krs: data.krs ?? null,
      regon: data.regon ?? null,
      country_code: data.country_code,
      address_l1: data.address_l1 ?? null,
      address_l2: data.address_l2 ?? null,
      address_correspondance_l1: data.address_correspondance_l1 ?? null,
      address_correspondance_l2: data.address_correspondance_l2 ?? null,
      email: data.email ?? null,
      phone_number: data.phone_number ?? null,
      additional_info: data.additional_info ?? null,
    });
  },
  onError: (error: number) => {
    if (error == 404) {
      toast.add({ severity: "error", summary: "Użytkownik nie ma dodanej firmy", life: 3000 });
    } else if (error == 409) {
      toast.add({
        severity: "warning",
        summary: "Firma użytkownika nie zautoryzowana w KSeF",
        life: 3000,
      });
    } else {
      toast.add({ severity: "error", summary: "Błąd podczas pobierania danych firmy", life: 3000 });
    }
  },
});

const updateCompanyMutation = useMutation({
  mutationFn: async (values: any) => {
    const companyResp = await updateCompany({
      id: props.companyInfo?.id,
      owner_id: props.userCompany ? currentUserStore.getUserId : null,
      name: values.name,
      nip: values.nip,
      krs: emptyToNull(values.krs),
      regon: emptyToNull(values.regon),
      country_code: values.countryCode,
      address_l1: emptyToNull(values.addressL1),
      address_l2: emptyToNull(values.addressL2),
      address_correspondance_l1: emptyToNull(values.addressCorrespondanceL1),
      address_correspondance_l2: emptyToNull(values.addressCorrespondanceL2),
      email: emptyToNull(values.email),
      phone_number: emptyToNull(values.phoneNumber),
      additional_info: emptyToNull(values.additionalInfo),
    });

    return companyResp;
  },

  onSuccess: () => {
    if (props.userCompany && props.createOrUpdate === "update") {
      getCompanyMutation.mutate();
    }
    toast.add({
      severity: "success",
      summary: "Dane firmy zaaktualizowane pomyślnie!",
      life: 3000,
    });
    emit("success");
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

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

const onFormSubmit = async (event: FormSubmitEvent) => {
  const { valid } = event;
  console.log(event.values);
  if (!valid) return;

  if (props.createOrUpdate === "update") updateCompanyMutation.mutate(event.values);
  if (props.createOrUpdate === "create") createCompanyMutation.mutate(event.values);
};

const isLoading = computed(
  () =>
    createCompanyMutation.isPending.value ||
    updateCompanyMutation.isPending.value ||
    getCompanyMutation.isPending.value ||
    getCountryCodesMutation.isPending.value,
);

watch(
  () => props.visible,
  async (visible) => {
    if (visible) {
      await getCountryCodesMutation.mutateAsync();
      if (props.createOrUpdate === "update") {
        formRef.value.states.countryCode.value = countries.value.find(
          (c) => c.value === props.companyInfo?.country_code,
        )?.value;
      } else {
        formRef.value.states.countryCode.value = countries.value.find(
          (c) => c.value === "PL",
        )?.value;
      }
    }
  },
);
</script>

<template>
  <Dialog
    :visible="visible"
    @update:visible="emit('update:visible', $event)"
    :closable="dialogClosable"
    modal
    :draggable="false"
    :style="{ width: '40rem' }"
  >
    <template #header>
      <div v-if="props.createOrUpdate === 'update'" class="flex flex-col text-xl font-semibold">
        <span v-if="userCompany">
          Edytuj dane firmy użytkownika {{ currentUserStore.getFullName }}:
        </span>
        <span v-else> Edytuj dane firmy: </span>
        <span class="font-semibold text-xl">
          {{ formRef?.states?.name?.value }}
        </span>
      </div>
      <div v-if="props.createOrUpdate === 'create'" class="flex flex-col text-xl font-semibold">
        <span v-if="userCompany">
          Dodaj firmę użytkownika: {{ currentUserStore.getFullName }}
        </span>
        <span v-else> Dodaj nową firmę </span>
      </div>
    </template>
    <span v-if="props.createOrUpdate === 'create'" class="flex pb-4"
      >Pola opcjonalne i dodatkowe informacje o firmie można zmienić później.</span
    >
    <div class="card flex justify-center pt-2">
      <Form
        ref="formRef"
        :resolver="resolver"
        @submit="onFormSubmit"
        disa
        class="flex flex-col gap-4 w-full items-center sm:w-150"
      >
        <div class="flex gap-4 w-full">
          <div class="flex flex-col gap-4 w-full">
            <FormField
              v-slot="$field"
              name="name"
              :initialValue="props.createOrUpdate === 'update' ? props.companyInfo?.name : ''"
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="name_input"
                  type="text"
                  fluid
                />
                <label for="name_input">Nazwa firmy</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField
              v-slot="$field"
              name="nip"
              :initialValue="props.createOrUpdate === 'update' ? props.companyInfo?.nip : ''"
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="nip_input"
                  type="text"
                  fluid
                />
                <label for="nip_input">NIP Firmy</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField
              v-slot="$field"
              name="krs"
              :initialValue="props.createOrUpdate === 'update' ? props.companyInfo?.krs : ''"
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="krs_input"
                  type="text"
                  fluid
                />
                <label for="krs_input">KRS Firmy (Opcjonalnie)</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField
              v-slot="$field"
              name="regon"
              :initialValue="props.createOrUpdate === 'update' ? props.companyInfo?.regon : ''"
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="regon_input"
                  type="text"
                  fluid
                />
                <label for="regon_input">REGON Firmy (Opcjonalnie)</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField
              v-slot="$field"
              name="email"
              :initialValue="props.createOrUpdate === 'update' ? props.companyInfo?.email : ''"
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="email_input"
                  type="text"
                  fluid
                />
                <label for="email_input">E-mail (Opcjonalnie)</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField
              v-slot="$field"
              name="phoneNumber"
              :initialValue="
                props.createOrUpdate === 'update' ? props.companyInfo?.phone_number : ''
              "
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="phoneNumber_input"
                  type="text"
                  fluid
                />
                <label for="phoneNumber_input">Telefon (Opcjonalnie)</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
          </div>
          <div class="flex flex-col gap-4 w-full">
            <FormField
              v-slot="$field"
              name="countryCode"
              :initialValue="
                props.createOrUpdate === 'update' ? props.companyInfo?.country_code : 'PL'
              "
            >
              <Select
                v-bind="$field.props"
                :options="countries"
                :disabled="userCompany || isLoading"
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
            <FormField
              v-slot="$field"
              name="addressL1"
              :initialValue="props.createOrUpdate === 'update' ? props.companyInfo?.address_l1 : ''"
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="addresL1_input"
                  type="text"
                  fluid
                />
                <label for="addresL1_input">Adres linia 1 (Opcjonalnie)</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField
              v-slot="$field"
              name="addressL2"
              :initialValue="props.createOrUpdate === 'update' ? props.companyInfo?.address_l2 : ''"
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="addresL2_input"
                  type="text"
                  fluid
                />
                <label for="addresL2_input">Adres linia 2 (Opcjonalnie)</label>
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField
              v-slot="$field"
              name="addressCorrespondanceL1"
              :initialValue="
                props.createOrUpdate === 'update'
                  ? props.companyInfo?.address_correspondance_l1
                  : ''
              "
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="addressCorrespondanceL1_input"
                  type="text"
                  fluid
                />
                <label for="addressCorrespondanceL1_input"
                  >Adres korespondencyjny linia 1 (Opcjonalnie)</label
                >
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField
              v-slot="$field"
              name="addressCorrespondanceL2"
              :initialValue="
                props.createOrUpdate === 'update'
                  ? props.companyInfo?.address_correspondance_l2
                  : ''
              "
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="addressCorrespondanceL2_input"
                  type="text"
                  fluid
                />
                <label for="addressCorrespondanceL2_input"
                  >Adres korespondencyjny linia 2 (Opcjonalnie)</label
                >
              </FloatLabel>
              <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
                $field.error?.message
              }}</Message>
            </FormField>
            <FormField
              v-slot="$field"
              name="additionalInfo"
              :initialValue="
                props.createOrUpdate === 'update' ? props.companyInfo?.additional_info : ''
              "
              class="flex flex-col gap-1"
            >
              <FloatLabel variant="on">
                <InputText
                  v-bind="$field.props"
                  :disabled="isLoading"
                  id="additionalInfo_input"
                  type="text"
                  fluid
                />
                <label for="additionalInfo_input">Dodatkowe informacje (Opcjonalnie)</label>
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
          :label="props.createOrUpdate === 'update' ? 'Zmień dane firmy' : 'Dodaj firmę'"
          :loading="updateCompanyMutation.isPending.value || createCompanyMutation.isPending.value"
          :disabled="updateCompanyMutation.isPending.value || createCompanyMutation.isPending.value"
          class="sm:w-100"
        />
      </Form>
    </div>
  </Dialog>
</template>
