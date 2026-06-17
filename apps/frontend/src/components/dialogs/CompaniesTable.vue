<script setup lang="ts">
import { ref, onMounted } from "vue";

import {
  DataTable,
  Column,
  useToast,
  InputText,
  IconField,
  InputIcon,
  FloatLabel,
  Button,
  Tag,
} from "primevue";
import { useMutation } from "@tanstack/vue-query";
import { useCurrentUserStore } from "../../stores/currentUserStore";
import { getCompaniesList, deleteCompany } from "../../lib/services/companyService";
import type { CompanyReadUpdate } from "../../lib/types/company";
import DeleteConfirmDialog from "./DeleteConfirmDialog.vue";
import CompanyForm from "../inputs/CompanyForm.vue";

const toast = useToast();
const currentUserStore = useCurrentUserStore();
const searchFilters = ref<string>("");
const lockedCompany = ref<CompanyReadUpdate[]>([]);
const expandedRows = ref<{ [key: string]: boolean }>({});
const sortedCompanies = ref<CompanyReadUpdate[]>([]);
const pageSize = ref(10);
const first = ref(0);
const totalRecords = ref(0);
const companyToEdit = ref<CompanyReadUpdate | null>(null);
const addCompanyDialog = ref(false);
const editCompanyDialog = ref(false);
const deleteCompanyDialog = ref(false);

const getCompaniesMutation = useMutation({
  mutationFn: async (values: any) => {
    const list_data = await getCompaniesList({
      search_string: values.search_string,
      page_size: values.page_size,
      page_offset: values.page_offset,
    });
    return list_data;
  },

  onSuccess: (data) => {
    // set the frozen top record as user company
    resetLockedUserCompanyRecord();
    // remove user company from the list of the rest of the companies
    sortedCompanies.value = data.companies.filter(
      (item: CompanyReadUpdate) => item.id !== currentUserStore.getCompanyId,
    );
    totalRecords.value = data.page_info.total_items;

    toast.add({ severity: "info", summary: "Pomyślnie pobrano firmy.", life: 3000 });
  },

  onError: (error) => {
    toast.add({
      severity: "error",
      summary: "Błąd w pobieraniu firm\n" + error?.response?.data?.detail,
      life: 5000,
    });
  },
});

const deleteCompanyMutation = useMutation({
  mutationFn: async (company: CompanyReadUpdate) => {
    const deletedCompanyResp = await deleteCompany(company.id);
    return company.id;
  },

  onSuccess: (deletedId) => {
    sortedCompanies.value = sortedCompanies.value.filter(
      (item: CompanyReadUpdate) => item.id !== deletedId,
    );
    deleteCompanyDialog.value = false;
    toast.add({ severity: "info", summary: "Pomyślnie usunięto firme.", life: 3000 });
  },

  onError: (error) => {
    toast.add({
      severity: "error",
      summary: "Błąd w usuwaniu firmy\n" + error?.response?.data?.detail,
      life: 5000,
    });
  },
});

function resetLockedUserCompanyRecord() {
  lockedCompany.value = [];
  lockedCompany.value.push(currentUserStore.getUserCompanyReadUpdate);
}

function onPageChange(event: any) {
  first.value = event.first;
  pageSize.value = event.rows;

  getCompaniesMutation.mutate({
    search_string: searchFilters.value,
    page_size: pageSize.value,
    page_offset: event.first,
  });
}

async function onSeachSubmit() {
  await getCompaniesMutation.mutate({
    search_string: searchFilters.value,
    page_size: pageSize.value,
    page_offset: 0,
  });
}

async function removeFilters() {
  searchFilters.value = "";
  first.value = 0;
  await getCompaniesMutation.mutate({
    search_string: searchFilters.value,
    page_size: pageSize.value,
    page_offset: 0,
  });
}

function addNewCompany() {
  addCompanyDialog.value = true;
}

async function editCompany(company: CompanyReadUpdate) {
  companyToEdit.value = null;
  companyToEdit.value = company;
  editCompanyDialog.value = true;
}

function confirmDeleteCompany(company: CompanyReadUpdate) {
  companyToEdit.value = null;
  companyToEdit.value = company;
  deleteCompanyDialog.value = true;
}

onMounted(() => {
  getCompaniesMutation.mutate({
    search_string: searchFilters.value,
    page_size: pageSize.value,
    page_offset: 0,
  });
});
</script>

<template>
  <DataTable
    :value="sortedCompanies"
    :loading="getCompaniesMutation.isPending.value"
    dataKey="id"
    :frozen-value="lockedCompany"
    v-model:expanded-rows="expandedRows"
    paginator
    paginator-position="bottom"
    :rows="pageSize"
    :first="first"
    :rows-per-page-options="[5, 10, 15, 25, 50]"
    :total-records="totalRecords"
    @page="onPageChange"
    lazy
    scroll-height="flex"
    scrollable
    scroll-direction="both"
    striped-rows
    :pt="{
      table: { style: 'min-width: 50rem;' },
      bodyrow: ({ props }) => ({
        class: [{ 'font-bold': props.frozenRow }],
      }),
      column: {
        bodycell: ({ state }) => ({
          style: state['d_editing'],
        }),
      },
    }"
  >
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span class="text-xl font-bold">Lista Firm</span>
        <div class="flex gap-2 items-center">
          <Button
            icon="pi pi-plus"
            rounded
            v-tooltip.bottom="'Dodaj nową firmę'"
            @click="addNewCompany"
          ></Button>
          <Button
            icon="pi pi-filter-slash"
            outlined
            v-tooltip.bottom="'Wyczysć filtry'"
            @click="removeFilters"
          ></Button>
          <FloatLabel variant="on">
            <IconField>
              <InputIcon>
                <i class="pi pi-search" />
              </InputIcon>
              <InputText
                id="on_label"
                maxlength="64"
                v-model="searchFilters"
                v-tooltip.bottom="
                  'Wyszukaj firmę po nazwie, NIP, adresie, e-mailu lub numerze telefonu. (Zatwierdź wyszukiwanie enterem)'
                "
                @keydown.enter="onSeachSubmit"
                :disabled="getCompaniesMutation.isPending.value"
              />
              <label for="on_label">Wyszukaj firmę</label>
            </IconField>
          </FloatLabel>
        </div>
      </div>
    </template>
    <template #empty> W bazie danych nie ma zapisanych innych firm. </template>
    <Column expander style="width: 1%"></Column>
    <Column field="name" header="Nazwa" style="width: 20%">
      <template #body="slotProps">
        <Tag v-if="slotProps.frozenRow" value="Moja firma" severity="info"></Tag>
        <span>{{ " " + slotProps.data.name }}</span>
      </template>
    </Column>
    <Column field="nip" header="NIP" style="width: 8%">
      <template #body="slotProps">
        <span>{{ slotProps.data.nip }}</span>
      </template>
    </Column>
    <Column field="address" header="Adres" style="width: 15%">
      <template #body="slotProps">
        <div class="flex items-center gap-2">
          <img
            v-if="!slotProps.data._flagError"
            :src="`https://flagcdn.com/${slotProps.data.country_code?.toLowerCase()}.svg`"
            style="width: 24px"
            loading="lazy"
            @error="
              () => {
                slotProps.data._flagError = true;
              }
            "
          />
          <div class="flex flex-col">
            <span>{{ slotProps.data.address_l1 }}</span>
            <span>{{ slotProps.data.address_l2 }}</span>
          </div>
        </div>
      </template>
    </Column>
    <Column field="email" header="E-mail" style="width: 10%">
      <template #body="slotProps">
        <span v-if="slotProps.data.email">{{ slotProps.data.email }}</span>
        <span v-else>-</span>
      </template>
    </Column>
    <Column field="phone_number" header="Nr. telefonu" style="width: 10%">
      <template #body="slotProps">
        <span v-if="slotProps.data.phone_number">{{ slotProps.data.phone_number }}</span>
        <span v-else>-</span>
      </template>
    </Column>
    <Column header="Edycja / Usuwanie" style="width: 10%">
      <template #body="slotProps">
        <Button
          icon="pi pi-pencil"
          variant="outlined"
          class="mr-2"
          @click="editCompany(slotProps.data)"
        />
        <Button
          icon="pi pi-trash"
          variant="outlined"
          severity="danger"
          @click="confirmDeleteCompany(slotProps.data)"
          :disabled="slotProps.data.id === currentUserStore.getCompanyId"
        /> </template
    ></Column>
    <template #expansion="slotProps">
      <div class="flex flex-row gap-40">
        <div class="flex flex-col gap-2 pl-18">
          <span class="font-semibold">KRS</span>
          <span>{{ slotProps.data.krs || "-" }}</span>
        </div>
        <div class="flex flex-col gap-2">
          <span class="font-semibold">REGON</span>
          <span>{{ slotProps.data.regon || "-" }}</span>
        </div>
        <div class="flex flex-col gap-2">
          <span class="font-semibold">Adres korespondencyjny</span>
          <div class="flex flex-col">
            <span>
              {{ slotProps.data.address_correspondance_l1 || "-" }}
            </span>
            <span>
              {{ slotProps.data.address_correspondance_l2 || "-" }}
            </span>
          </div>
        </div>
        <div class="flex flex-col gap-2 max-w-200">
          <span class="font-semibold">Dodatkowe informacje</span>
          <span class="wrap-break-word">{{ slotProps.data.additional_info || "-" }}</span>
        </div>
      </div>
    </template>
  </DataTable>
  <!-- Company create dialog -->
  <CompanyForm
    v-model:visible="addCompanyDialog"
    createOrUpdate="create"
    :user-company="false"
    :companyInfo="null"
    :loading="getCompaniesMutation.isPending.value"
    @success="
      () => {
        removeFilters();
        addCompanyDialog = false;
      }
    "
    @cancel="addCompanyDialog = false"
  />

  <!-- Company edit dialog -->
  <CompanyForm
    v-model:visible="editCompanyDialog"
    createOrUpdate="update"
    :user-company="companyToEdit?.id === currentUserStore.getCompanyId"
    :companyInfo="companyToEdit"
    :loading="getCompaniesMutation.isPending.value"
    @success="
      () => {
        removeFilters();
        editCompanyDialog = false;
        expandedRows = {};
        companyToEdit = null;
      }
    "
    @cancel="editCompanyDialog = false"
  />

  <!-- Company delete dialog -->
  <DeleteConfirmDialog
    v-model:visible="deleteCompanyDialog"
    :deletionObjectName="companyToEdit?.name"
    deleteObjectString="firmę"
    :loading="deleteCompanyMutation.isPending.value"
    @confirm="deleteCompanyMutation.mutate(companyToEdit)"
    @cancel="deleteCompanyDialog = false"
  />
</template>
