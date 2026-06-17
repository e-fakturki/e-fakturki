<script setup lang="ts">
import {
  Button,
  Dialog,
  Card,
  Tag,
  Popover,
  DataTable,
  Column,
  Divider,
  Select,
  useToast,
} from "primevue";
import invoiceXml from "../../assets/mock_xml";
import { emptyToNull, formatDisplayDate, formatPLN, parsePolishDateTime } from "../../lib/utils";
import { ref, watch } from "vue";
import { useMutation } from "@tanstack/vue-query";
import { getInvoiceDetails, postInvoiceXmlToKsef } from "../../lib/services/ksefService";
import type { InvoiceCompanyData, InvoiceObject } from "../../lib/types/invoices";
import {
  ksefStatusHint,
  ksefStatusSeverity,
  paymentType,
  paymentStatusSeverity,
  paymentStatusMapForComponents,
  paymentStatus,
} from "../../lib/types/invoices";
import type { invoiceTableType } from "../../lib/types/invoices";
import { useCurrentUserStore } from "../../stores/currentUserStore";
import { createCompany } from "../../lib/services/companyService";

const props = defineProps<{
  visible: boolean;
  invoice: any;
  invoice_type: invoiceTableType;
  invoice_creation: boolean;
}>();

const toast = useToast();
const currentUserStore = useCurrentUserStore();
const ksefPopup = ref();
const toggleKsefPopup = (event: any) => {
  ksefPopup.value.toggle(event);
};
const emit = defineEmits(["update:visible"]);
const invoiceData = ref<InvoiceObject | null>(null);
const postInvoiceToKsefError = ref<string>("");

const getInvoiceDetailsMutation = useMutation({
  mutationFn: async (values: any) => {
    const list_data = await getInvoiceDetails(values.company_id, values.invoice_id);
    return list_data;
  },

  onSuccess: (data) => {
    invoiceData.value = structuredClone(data);
  },

  onError: (data) => {
    toast.add({ severity: "error", summary: "Błąd w danych faktury." + data, life: 3000 });
  },
});

const postInvoiceToKsefMutation = useMutation({
  mutationFn: async () => {
    const status = await postInvoiceXmlToKsef(currentUserStore.getCompanyId, props.invoice.id);
    return status;
  },

  onSuccess: (data) => {
    if (invoiceData.value) {
      invoiceData.value.ksef_number = data.ksef_number;
      invoiceData.value.invoicing_date = data.invoicing_date;
      invoiceData.value.acquisition_date = data.acquisition_date;
      invoiceData.value.permanent_storage_date = data.permanent_storage_date;
    }
    toast.add({ severity: "info", summary: "Pomyślnie wysłano fakturę do KSeF.", life: 3000 });
  },

  onError: (data) => {
    toast.add({
      severity: "error",
      summary: "Błąd podczas wysyłania faktury do KSeF." + data,
      life: 3000,
    });
    postInvoiceToKsefError.value = data.message;
  },
});

const saveCompanyMutation = useMutation({
  mutationFn: async () => {
    const company =
      props.invoice_type === "sales"
        ? invoiceData.value?.buyer_info
        : invoiceData.value?.seller_info;

    const companyResp = await createCompany({
      owner_id: null,
      name: company?.name,
      nip: company?.nip,
      krs: emptyToNull(company?.krs),
      regon: emptyToNull(company?.regon),
      country_code: company?.country_code || "PL",
      address_l1: emptyToNull(company?.address_l1),
      address_l2: emptyToNull(company?.address_l2),
      address_correspondance_l1: emptyToNull(company?.address_correspondance_l1),
      address_correspondance_l2: emptyToNull(company?.address_correspondance_l2),
      email: emptyToNull(company?.email),
      phone_number: emptyToNull(company?.phone),
      additional_info: null,
    });

    return companyResp;
  },

  onSuccess: () => {
    toast.add({ severity: "success", summary: "Firma dodana pomyślnie!", life: 3000 });
  },

  onError: (error) => {
    toast.add({
      severity: "info",
      summary: error?.response?.data?.detail,
      life: 5000,
    });
  },
});

function collectAddress(companyInfo: InvoiceCompanyData) {
  return [companyInfo.address_l1, companyInfo.address_l2].filter(Boolean).join(", ");
}

function createFileName(inv: any) {
  return inv.invoice_number.trim().replace(/\s+/g, "_");
}

function onDownloadXml(fileName: string) {
  // call API to get the XML
  const xml = invoiceXml;

  const blob = new Blob([xml], { type: "application/xml" });
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;

  document.body.appendChild(a);
  a.click();

  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

function onDownloadPdf() {}

function onPrintPdf() {}

watch(
  () => props.visible,
  async (visible) => {
    if (visible) {
      if (props.invoice_creation) {
        // For new invoices, directly use props.invoice (handle both ref and direct value)
        invoiceData.value = props.invoice?.value ?? props.invoice;
      } else if (props.invoice?.id) {
        // For existing invoices, fetch from API
        await getInvoiceDetailsMutation.mutateAsync({
          company_id: currentUserStore.getCompanyId,
          invoice_id: props.invoice.id,
        });
      }
    }
  },
);
</script>

<template>
  <Dialog
    :visible="visible"
    position="bottom"
    @update:visible="emit('update:visible', $event)"
    @hide="
      () => {
        invoiceData.value = null;
      }
    "
    modal
    maximizable
    :style="{ width: '60%' }"
    :loading="getInvoiceDetailsMutation.isPending.value"
  >
    <!-- header -->
    <template #header>
      <div v-if="invoiceData" class="flex-1 flex gap-4 items-center">
        <Tag v-if="invoiceData.is_new" value="Nowa"></Tag>
        <span class="text-xl font-bold">
          {{ `Faktura ${invoiceData.invoice_type.toUpperCase()} nr ${invoiceData.invoice_number}` }}
        </span>
        <Tag
          :value="ksefStatusHint[invoiceData.ksef_status]"
          :severity="ksefStatusSeverity[invoiceData.ksef_status]"
        ></Tag>
        <div v-if="!props.invoice_creation">
          <Button
            v-if="invoiceData.ksef_status === 'accepted' || invoiceData.ksef_status === 'rejected'"
            icon="pi pi-info-circle"
            outlined
            v-tooltip.top="'Szczegóły'"
            @click="toggleKsefPopup"
            :loading="postInvoiceToKsefMutation.isPending.value"
            :disabled="postInvoiceToKsefMutation.isPending.value"
          ></Button>
          <Button
            v-if="invoiceData.ksef_status === 'not_sent' || invoiceData.ksef_status === 'rejected'"
            icon="pi pi-send"
            outlined
            v-tooltip.top="'Wyślij do KSeF'"
            @click="postInvoiceToKsefMutation.mutate"
            :loading="postInvoiceToKsefMutation.isPending.value"
            :disabled="postInvoiceToKsefMutation.isPending.value"
          ></Button>
        </div>
      </div>
    </template>

    <!-- content -->
    <div v-if="invoiceData" class="mr-4 ml-4">
      <!-- issue date and place -->
      <div class="flex-1 flex flex-col text-end">
        <span>Miejsce i data wystawienia: </span>
        <div>
          <span class="font-semibold">
            {{ invoiceData.issue_place ? `${invoiceData.issue_place}, ` : "-, " }}
          </span>
          <span v-if="!invoice_creation" class="font-semibold">
            {{ new Date(invoiceData.issue_date).toLocaleDateString() }}
          </span>
          <span v-else class="font-semibold">
            {{ parsePolishDateTime(invoiceData.issue_date).toLocaleDateString() }}
          </span>
        </div>
      </div>
      <!-- companies info -->
      <div class="flex-1 flex justify-between mt-4 mb-8">
        <Card>
          <template #title>Sprzedawca</template>
          <template #content>
            <p class="m-0">{{ invoiceData.seller_info.name }}</p>
            <p class="m-0">NIP {{ invoiceData.seller_info.nip }}</p>
            <p class="m-0">{{ collectAddress(invoiceData.seller_info) }}</p>
          </template>
        </Card>
        <div
          class="flex flex-1 items-start"
          :class="props.invoice_type === 'sales' ? 'justify-end pr-2' : 'justify-start pl-2'"
        >
          <Button
            icon="pi pi-save"
            outlined
            v-tooltip.top="'Zapisz firmę w bazie danych'"
            @click="saveCompanyMutation.mutate"
            :loading="saveCompanyMutation.isPending.value"
            :disabled="saveCompanyMutation.isPending.value"
          ></Button>
        </div>
        <Card>
          <template #title>Nabywca</template>
          <template #content>
            <p class="m-0">{{ invoiceData.buyer_info.name }}</p>
            <p class="m-0">NIP {{ invoiceData.buyer_info.nip }}</p>
            <p class="m-0">{{ collectAddress(invoiceData.buyer_info) }}</p>
          </template>
        </Card>
      </div>
      <!-- invoice items -->
      <DataTable :value="invoiceData.entries || []">
        <Column field="row_number" header="Lp." style="width: 2%"></Column>
        <Column field="name" header="Nazwa towaru lub usługi" style="width: 25%"></Column>
        <Column field="amount" header="Ilość + J.m." style="width: 12%">
          <template #body="slotProps">
            <span>{{ slotProps.data.amount + " " + slotProps.data.unit }}</span>
          </template>
        </Column>
        <Column field="net_price" header="Cena netto" style="width: 10%">
          <template #body="slotProps">
            <span v-if="slotProps.data.net_price">{{
              formatPLN(slotProps.data.net_price || 0)
            }}</span>
            <span v-else>-</span>
          </template>
          <template #footer>
            <span class="font-semibold"> SUMA: </span>
          </template>
        </Column>
        <Column field="net_total" header="Wartość netto" style="width: 10%">
          <template #body="slotProps">
            <span v-if="slotProps.data.net_total">{{
              formatPLN(slotProps.data.net_total || 0)
            }}</span>
            <span v-else>-</span>
          </template>
          <template #footer>
            <span class="font-semibold">
              {{ formatPLN(invoiceData.net_total || 0) }}
            </span>
          </template>
        </Column>
        <Column field="tax_rate" header="Stawka VAT" style="width: 7%">
          <template #body="slotProps">
            <span>{{
              props.invoice_creation
                ? slotProps.data.tax_rate.display_text
                : slotProps.data.tax_rate + "%"
            }}</span>
          </template>
        </Column>
        <Column field="tax_total" header="Wartość VAT" style="width: 10%">
          <template #body="slotProps">
            <span v-if="slotProps.data.tax_total">{{
              formatPLN(slotProps.data.tax_total || 0)
            }}</span>
            <span v-else>-</span>
          </template>
          <template #footer>
            <span v-if="invoiceData.tax_total" class="font-semibold">
              {{ formatPLN(invoiceData.tax_total || 0) }}
            </span>
            <span v-else>-</span>
          </template>
        </Column>
        <Column
          v-if="invoiceData.entries[0]?.gross_price"
          field="gross_price"
          header="Cena brutto"
          style="width: 10%"
        >
          <template #body="slotProps">
            <span v-if="slotProps.data.gross_price">{{
              formatPLN(slotProps.data.gross_price || 0)
            }}</span>
            <span v-else>-</span>
          </template>
        </Column>
        <Column field="gross_total" header="Wartość brutto" style="width: 10%">
          <template #body="slotProps">
            <span v-if="slotProps.data.gross_total">{{
              formatPLN(slotProps.data.gross_total || 0)
            }}</span>
            <span v-else>-</span>
          </template>
          <template #footer>
            <span class="font-semibold">
              {{ formatPLN(invoiceData.gross_total || 0) }}
            </span>
          </template>
        </Column>
      </DataTable>
      <!-- summary -->
      <div class="mt-4">
        <Card>
          <template #title
            >Do zapłaty:&nbsp;&nbsp;{{ formatPLN(invoiceData?.gross_total || 0) }}</template
          >
          <template #content>
            <!-- <span>{{ "słownie: " }}</span> -->
          </template>
        </Card>
      </div>

      <!-- payment info -->
      <Divider />
      <div v-if="invoiceData.payment" class="flex mt-4">
        <!-- left info -->
        <div class="flex-1 flex flex-col text-start">
          <span>Rodzaj płatności: </span>
          <span class="font-semibold">
            {{ paymentType[invoiceData.payment.payment_type] }}
          </span>
          <div v-if="invoiceData.payment.payment_due_date">
            <span>Termin płatności: </span>
            <span class="font-semibold">
              {{
                invoice_creation
                  ? parsePolishDateTime(invoiceData.payment.payment_due_date).toLocaleDateString()
                  : new Date(invoiceData.payment.payment_due_date).toLocaleDateString()
              }}
            </span>
          </div>
          <div v-else-if="invoiceData.payment.payment_date">
            <span>Data płatności: </span>
            <span class="font-semibold">
              {{
                invoice_creation
                  ? parsePolishDateTime(invoiceData.payment.payment_date).toLocaleDateString()
                  : new Date(invoiceData.payment.payment_date).toLocaleDateString()
              }}
            </span>
          </div>
          <div class="mt-2">
            <span>Dane płatności: </span>
            <div>
              <span>Numer konta: </span>
              <span v-if="invoiceData.payment.seller_bank_account_number" class="font-semibold">
                {{ invoiceData.payment.seller_bank_account_number }}
              </span>
              <span v-else class="font-semibold">-</span>
            </div>
            <div>
              <span>Bank: </span>
              <span v-if="invoiceData.payment.seller_bank_name" class="font-semibold">
                {{ invoiceData.payment.seller_bank_name }}
              </span>
              <span v-else class="font-semibold">-</span>
            </div>
          </div>
        </div>
        <!-- right status -->
        <div class="flex-1 flex justify-end items-start gap-4">
          <div class="flex gap-4 items-center">
            <Select
              v-if="!props.invoice_creation"
              v-model="invoiceData.payment.payment_status"
              :options="paymentStatusMapForComponents"
              optionLabel="label"
              optionValue="value"
              placeholder="Wybierz status płatności"
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
                <span v-else class="text-gray-400"> Wybierz status płatności </span>
              </template>
            </Select>
            <Tag
              v-else
              :value="paymentStatus[invoiceData.payment.payment_status]"
              :severity="paymentStatusSeverity[invoiceData.payment.payment_status]"
            />
          </div>
        </div>
      </div>
      <Divider />

      <!-- additional info -->
      <div class="flex-1 flex flex-col gap-4">
        <div class="flex-1 flex flex-col">
          <span>Adnotacje: </span>
          <span class="font-semibold">
            {{ invoiceData.annotations || "-" }}
          </span>
        </div>
        <div class="flex-1 flex flex-col">
          <span>Rejestry: </span>
          <span class="font-semibold">
            {{ invoiceData.footer_registers || "-" }}
          </span>
        </div>
        <div class="flex-1 flex flex-col">
          <span>Dodatkowe informacje: </span>
          <span class="font-semibold">
            {{ invoiceData.additional_info || "-" }}
          </span>
          <span class="font-semibold">
            {{ invoiceData.footer_info || "-" }}
          </span>
        </div>
      </div>
    </div>

    <template #footer v-if="invoiceData">
      <Button
        label="Pobierz XML"
        icon="pi pi-download"
        outlined
        @click="() => onDownloadXml(createFileName(invoiceData))"
      ></Button>
      <Button
        disabled
        label="Pobierz PDF"
        icon="pi pi-file-pdf"
        outlined
        @click="onDownloadPdf"
      ></Button>
      <Button disabled label="Drukuj" icon="pi pi-print" outlined @click="onPrintPdf"></Button>
    </template>
  </Dialog>

  <!-- ksef popup -->
  <Popover ref="ksefPopup">
    <div v-if="invoiceData?.ksef_status === 'accepted'" class="flex flex-col w-130">
      <div>
        <span>Numer KSeF: </span>
        <span class="font-semibold">{{ invoiceData?.ksef_number }}</span>
      </div>
      <div>
        <span>Data przyjęcia faktury w systemie KSeF: </span>
        <span class="font-semibold">{{
          new Date(invoiceData?.invoicing_date).toLocaleString("pl-PL", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
          })
        }}</span>
      </div>
      <div>
        <span>Data nadania numeru KSeF: </span>
        <span class="font-semibold">{{
          new Date(invoiceData?.acquisition_date).toLocaleString("pl-PL", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
          })
        }}</span>
      </div>
      <div>
        <span>Data trwałego zapisu faktury w KSeF: </span>
        <span class="font-semibold">{{
          new Date(invoiceData?.permanent_storage_date).toLocaleString("pl-PL", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
          })
        }}</span>
      </div>
    </div>
    <div v-if="invoiceData?.ksef_status === 'rejected'" class="flex flex-col w-130">
      <span>Szczegóły odrzucenia faktury przez KSeF: </span>
      <span class="font-semibold">{{ postInvoiceToKsefError }}</span>
    </div>
  </Popover>
</template>
