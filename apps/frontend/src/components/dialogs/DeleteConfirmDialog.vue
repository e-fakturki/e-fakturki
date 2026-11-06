<script setup lang="ts">
import { Dialog, Button } from "primevue";
import type { CompanyListItem } from "../../lib/types/company";

type DeletionStringType = "firmę" | "produkt" | "kategorię" | "fakturę" | "konto" | "rekord";

const props = defineProps<{
  visible: boolean;
  loading?: boolean;
  title?: string;
  deletionObjectName: any | CompanyListItem;
  deleteObjectString: DeletionStringType;
}>();
const emit = defineEmits(["update:visible", "confirm", "cancel"]);
</script>

<template>
  <Dialog
    :visible="visible"
    :draggable="false"
    :style="{ width: '450px' }"
    :header="title || 'Potwierdź'"
    modal
    @update:visible="emit('update:visible', $event)"
  >
    <div class="flex items-center gap-4">
      <i class="pi pi-exclamation-triangle text-3xl!" />
      <div v-if="deletionObjectName" class="flex flex-col">
        <span>{{ `Czy napewno chcesz usunąć ${props.deleteObjectString}: ` }}</span>
        <span class="font-semibold">{{ deletionObjectName + `?` }}</span>
      </div>
    </div>
    <template #footer>
      <Button
        label="Nie"
        icon="pi pi-times"
        severity="secondary"
        variant="text"
        :disabled="loading"
        @click="emit('cancel')"
      />
      <Button
        label="Tak"
        icon="pi pi-check"
        severity="danger"
        outlined
        :disabled="loading"
        @click="emit('confirm')"
      />
    </template>
  </Dialog>
</template>
