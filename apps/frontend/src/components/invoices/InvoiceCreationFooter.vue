<script setup lang="ts">
import { Button, Toolbar } from "primevue";

const props = defineProps<{
  disabled: boolean;
}>();
const emits = defineEmits(["clear", "preview", "save", "saveAndSend"]);
</script>

<template>
  <Toolbar>
    <template #start>
      <div class="flex gap-4">
        <Button
          label="Wyczyść dane faktury"
          icon="pi pi-eraser"
          raised
          outlined
          severity="danger"
          @click="emits('clear')"
        />
      </div>
    </template>

    <template #end>
      <div class="flex gap-4">
        <Button
          label="Podgląd faktury"
          icon="pi pi-eye"
          raised
          outlined
          severity="info"
          :disabled="props.disabled"
          @click="emits('preview')"
        />

        <Button
          label="Zapisz fakturę"
          icon="pi pi-save"
          raised
          severity="success"
          :disabled="props.disabled"
          @click="emits('save')"
        />

        <Button
          label="Wyślij fakturę do KSeF"
          icon="pi pi-cloud-upload"
          raised
          severity="danger"
          :disabled="props.disabled"
          @click="emits('saveAndSend')"
        />
      </div>
    </template>
  </Toolbar>
</template>
