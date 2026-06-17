<script setup lang="ts">
import { Dialog, Button, Message, FloatLabel, Password } from "primevue";
import { Form, FormField, type FormSubmitEvent } from "@primevue/forms";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import { useMutation } from "@tanstack/vue-query";
import { useToast } from "primevue/usetoast";
import { computed, ref } from "vue";
import { z } from "zod";

import AppLogo from "../AppLogo.vue";
import FileInput from "../inputs/FileInput.vue";
import type { KsefCredentials } from "../../lib/types/ksef";
import { useCurrentUserStore } from "../../stores/currentUserStore";
import { createKsefCredentials } from "../../lib/services/ksefService";

const toast = useToast();
const currentUserStore = useCurrentUserStore();

const emit = defineEmits(["update:visible", "success"]);

const resolver = zodResolver(
  z.object({
    ksef_password: z.string().min(1, { message: "Hasło jest wymagane." }),
  }),
);

const createKsefCredsMutation = useMutation({
  mutationFn: async (values: any) => {
    const companyId = currentUserStore.getCompanyId;
    if (!companyId) {
      throw new Error("Brak companyId");
    }

    return await createKsefCredentials({
      company_id: companyId,
      online_certificates: true,
      certificate: values.certFile,
      private_key: values.keyFile,
      password: values.certPassword,
    });
  },

  onSuccess: () => {
    toast.add({
      severity: "success",
      summary: "Poprawnie uwierzytelniono firmę w KSeF!",
      life: 3000,
    });
    currentUserStore.setCompanyKsefAuthorizationStatus(true);
    emit("success");
  },

  onError: () => {
    toast.add({ severity: "error", summary: "Coś poszło nie tak", life: 3000 });
  },
});

const selectedCertFile = ref<File | null>(null);
const selectedKeyFile = ref<File | null>(null);

function handleSelectCert(file: File) {
  selectedCertFile.value = file;
}
function handleClearCert() {
  selectedCertFile.value = null;
}
function handleSelectKey(file: File) {
  selectedKeyFile.value = file;
}
function handleClearKey() {
  selectedKeyFile.value = null;
}

function areFilesSelected(): boolean {
  if (!selectedCertFile.value || !selectedKeyFile.value) {
    toast.add({
      severity: "error",
      summary: "Brak plików",
      detail: "Dodaj certyfikat i klucz",
      life: 3000,
    });
    return false;
  }
  return true;
}

const onFormSubmit = (event: FormSubmitEvent) => {
  const { valid } = event;
  if (!valid) return;
  if (!areFilesSelected()) return;

  const payload: KsefCredentials = {
    certFile: selectedCertFile.value,
    keyFile: selectedKeyFile.value,
    certPassword: event.values.ksef_password,
  };

  createKsefCredsMutation.mutate(payload);
};

const companyName = computed(() => currentUserStore.getCompanyName);
</script>

<template>
  <Dialog
    :visible="true"
    @update:visible="emit('update:visible', $event)"
    modal
    :draggable="false"
    :style="{ width: '40rem' }"
  >
    <template #header>
      <AppLogo />
    </template>
    <span class="block mb-2 font-semibold">
      Uwierzytelnij firmę {{ companyName }} w systemie KSeF.
    </span>
    <span class="block mb-5 text-sm text-gray-500">
      Upewnij się, że przesłane pliki służą do uwierzytelniania w KSeF, a nie do podpisu offline.
      Jeśli nie posiadasz jeszcze certyfikatów KSeF, wygeneruj je zgodnie z instrukcją:
      <a
        href="https://www.youtube.com/watch?v=SE0IHuPHtRE"
        target="_blank"
        class="text-sky-600 underline hover:text-primary-600"
      >
        Zobacz poradnik
      </a>
    </span>
    <div class="card flex justify-center">
      <Form :resolver @submit="onFormSubmit" class="flex flex-col gap-4 w-full sm:w-100">
        <FileInput
          acceptableFiles=".pfx,.crt,.cer"
          credentials
          :maxFileSize="1000000"
          invalidFileTypeMessage="Błędny typ pliku. (Akceptowalne: *.crt, *.pfx, *.cer)"
          dragAndDropMessage="Przeciągnij i upuść certyfikat uwierzytelniający. (np. plik auth.crt)"
          fileIcon="pi-file-check"
          @file-selected="handleSelectCert"
          @file-removed="handleClearCert"
        />
        <FileInput
          acceptableFiles=".key"
          credentials
          :maxFileSize="1000000"
          invalidFileTypeMessage="Błędny typ pliku. (Akceptowalne: *.key)"
          dragAndDropMessage="Przeciągnij i upuść klucz dla certyfikatu uwierzytelniającego. (np. plik
                auth.key)"
          fileIcon="pi-key"
          @file-selected="handleSelectKey"
          @file-removed="handleClearKey"
        />
        <FormField v-slot="$field" name="ksef_password" class="flex flex-col gap-1" initialValue="">
          <FloatLabel variant="on">
            <Password
              v-bind="$field.props"
              id="password_input"
              type="text"
              :feedback="false"
              toggleMask
              fluid
            />
            <label for="password_input">Hasło do klucza uwierzytelniającego KSeF</label>
          </FloatLabel>
          <Message v-if="$field?.invalid" severity="error" size="small" variant="simple">{{
            $field.error?.message
          }}</Message>
        </FormField>
        <Button
          type="submit"
          severity="secondary"
          label="Uwierzytelnij firmę w KSeF"
          :loading="createKsefCredsMutation.isPending.value"
          :disabled="createKsefCredsMutation.isPending.value"
        />
      </Form>
    </div>
  </Dialog>
</template>
