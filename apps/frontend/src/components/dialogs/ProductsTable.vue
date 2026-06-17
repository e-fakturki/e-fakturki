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
} from "primevue";
import { useMutation } from "@tanstack/vue-query";
import { useCurrentUserStore } from "../../stores/currentUserStore";
import DeleteConfirmDialog from "./DeleteConfirmDialog.vue";
import ProductForm from "../inputs/ProductForm.vue";
import type { ProductListItem, TaxRate } from "../../lib/types/products";
import { deleteProduct, getProductsList, getTaxRates } from "../../lib/services/productService";
import { formatPLN } from "../../lib/utils.ts";

const toast = useToast();
const currentUserStore = useCurrentUserStore();
const searchFilters = ref<string>("");
const expandedRows = ref<{ [key: string]: boolean }>({});
const sortedProducts = ref<ProductListItem[]>([]);
const taxRates = ref<TaxRate[]>([]);
const taxRateMap = ref<Map<string, TaxRate>>(new Map());
const pageSize = ref(10);
const first = ref(0);
const totalRecords = ref(0);
const productToEdit = ref<ProductListItem | null>(null);
const addProductDialog = ref(false);
const editProductDialog = ref(false);
const deleteProductDialog = ref(false);

const getProductsMutation = useMutation({
  mutationFn: async (values: any) => {
    const list_data = await getProductsList({
      company_id: currentUserStore.getCompanyId,
      search_string: values.search_string,
      page_size: values.page_size,
      page_offset: values.page_offset,
    });
    return list_data;
  },

  onSuccess: (data) => {
    totalRecords.value = data.page_info.total_items;
    sortedProducts.value = data.products;
    toast.add({ severity: "info", summary: "Pomyślnie pobrano produkty.", life: 3000 });
  },

  onError: (error) => {
    toast.add({
      severity: "error",
      summary: "Błąd w pobieraniu produktów\n" + error?.response?.data?.detail,
      life: 5000,
    });
  },
});

const deleteProductMutation = useMutation({
  mutationFn: async (product: ProductListItem) => {
    const deletedProductResp = await deleteProduct(product.id);
    return product.id;
  },

  onSuccess: () => {
    refreshList();
    toast.add({ severity: "info", summary: "Pomyślnie usunięto produkt.", life: 3000 });
  },

  onError: (error) => {
    toast.add({
      severity: "error",
      summary: "Błąd w usuwaniu produktu\n" + error?.response?.data?.detail,
      life: 5000,
    });
  },
});

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

function onPageChange(event: any) {
  first.value = event.first;
  pageSize.value = event.rows;

  getProductsMutation.mutate({
    search_string: searchFilters.value,
    page_size: pageSize.value,
    page_offset: event.first,
  });
}

async function onSeachSubmit() {
  await getProductsMutation.mutate({
    search_string: searchFilters.value,
    page_size: pageSize.value,
    page_offset: 0,
  });
}

async function refreshList() {
  searchFilters.value = "";
  first.value = 0;
  addProductDialog.value = false;
  editProductDialog.value = false;
  deleteProductDialog.value = false;
  await getProductsMutation.mutate({
    search_string: searchFilters.value,
    page_size: pageSize.value,
    page_offset: 0,
  });
}

onMounted(() => {
  getTaxRatesMutation.mutate();
  getProductsMutation.mutate({
    search_string: searchFilters.value,
    page_size: pageSize.value,
    page_offset: 0,
  });
});
</script>

<template>
  <DataTable
    :value="sortedProducts"
    :loading="getProductsMutation.isPending.value"
    dataKey="id"
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
      column: {
        bodycell: ({ state }) => ({
          style: state['d_editing'],
        }),
      },
    }"
  >
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <span class="text-xl font-bold">Lista Produktów</span>
        <div class="flex gap-2 items-center">
          <Button
            icon="pi pi-plus"
            rounded
            v-tooltip.bottom="'Dodaj nowy produkt'"
            @click="
              () => {
                addProductDialog = true;
              }
            "
          ></Button>
          <Button
            icon="pi pi-filter-slash"
            outlined
            v-tooltip.bottom="'Wyczysć filtry'"
            @click="refreshList"
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
                  'Wyszukaj produkt po nazwie, opisie, GTIN. (Zatwierdź wyszukiwanie enterem)'
                "
                @keydown.enter="onSeachSubmit"
                :disabled="getProductsMutation.isPending.value"
              />
              <label for="on_label">Wyszukaj produkt</label>
            </IconField>
          </FloatLabel>
        </div>
      </div>
    </template>
    <template #empty> W bazie danych nie ma zapisanych żadnych produktów. </template>
    <Column expander style="width: 1%"></Column>
    <Column field="name" header="Nazwa" style="width: 10%">
      <template #body="slotProps">
        <span>{{ " " + slotProps.data.name }}</span>
      </template>
    </Column>
    <Column field="gtin" header="GTIN" style="width: 10%">
      <template #body="slotProps">
        <span v-if="slotProps.data.gtin">{{ slotProps.data.gtin }}</span>
        <span v-else>-</span>
      </template>
    </Column>
    <Column field="unit" header="Jednostka miary" style="width: 10%">
      <template #body="slotProps">
        <span v-if="slotProps.data.unit">{{ slotProps.data.unit }}</span>
        <span v-else>-</span>
      </template>
    </Column>
    <Column field="net_price" header="Cena netto" style="width: 10%">
      <template #body="slotProps">
        <span v-if="slotProps.data.net_price">{{ formatPLN(slotProps.data.net_price) }} </span>
        <span v-else>-</span>
      </template>
    </Column>
    <Column field="tax_rate" header="Stawka podatku" style="width: 10%">
      <template #body="slotProps">
        <span
          v-if="slotProps.data.tax_rate"
          v-tooltip.right="taxRateMap.get(slotProps.data.tax_rate)?.hint_text"
          >{{
            taxRateMap.get(slotProps.data.tax_rate)?.display_text || slotProps.data.tax_rate
          }}</span
        >
        <span v-else>-</span>
      </template>
    </Column>
    <Column field="gross_price" header="Cena brutto" style="width: 10%">
      <template #body="slotProps">
        <span v-if="slotProps.data.gross_price">{{ formatPLN(slotProps.data.gross_price) }}</span>
        <span v-else>-</span>
      </template>
    </Column>
    <Column header="Edycja / Usuwanie" style="width: 10%">
      <template #body="slotProps">
        <Button
          icon="pi pi-pencil"
          variant="outlined"
          class="mr-2"
          @click="
            () => {
              productToEdit = null;
              productToEdit = slotProps.data;
              editProductDialog = true;
            }
          "
        />
        <Button
          icon="pi pi-trash"
          variant="outlined"
          severity="danger"
          @click="
            () => {
              productToEdit = null;
              productToEdit = slotProps.data;
              deleteProductDialog = true;
            }
          "
        /> </template
    ></Column>
    <template #expansion="slotProps">
      <div class="flex flex-row gap-40">
        <div class="flex flex-col gap-2 pl-18">
          <span class="font-semibold">Opis produktu</span>
          <span>{{ slotProps.data.description || "-" }}</span>
        </div>
      </div>
    </template>
  </DataTable>
  <!-- Product create dialog -->
  <ProductForm
    v-model:visible="addProductDialog"
    createOrUpdate="create"
    :productInfo="null"
    :taxRates="taxRates"
    :loading="getProductsMutation.isPending.value"
    @success="
      () => {
        refreshList();
        addProductDialog = false;
      }
    "
    @cancel="addProductDialog = false"
  />

  <!-- Product edit dialog -->
  <ProductForm
    v-model:visible="editProductDialog"
    createOrUpdate="update"
    :productInfo="productToEdit"
    :taxRates="taxRates"
    :loading="getProductsMutation.isPending.value"
    @success="
      () => {
        refreshList();
        editProductDialog = false;
      }
    "
    @cancel="editProductDialog = false"
  />

  <!-- Product delete dialog -->
  <DeleteConfirmDialog
    v-model:visible="deleteProductDialog"
    :deletionObjectName="productToEdit?.name"
    deleteObjectString="produkt"
    :loading="deleteProductMutation.isPending.value"
    @confirm="deleteProductMutation.mutate(productToEdit)"
    @cancel="deleteProductDialog = false"
  />
</template>
