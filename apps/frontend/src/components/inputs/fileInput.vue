<script setup lang="ts">
import { Button, FileUpload } from "primevue";
import { ref } from "vue";

const props = defineProps<{
  acceptableFiles: string;
  credentials: boolean;
  maxFileSize: number;
  invalidFileTypeMessage: string;
  dragAndDropMessage: string;
  fileIcon: string;
}>();

const emit = defineEmits<{
  (e: "file-selected", file: File): void;
  (e: "file-removed"): void;
}>();

const isFileChosen = ref(false);
</script>

<template>
  <FileUpload
    :disabled="isFileChosen"
    :withCredentials="props.credentials"
    :showCancelButton="false"
    :showUploadButton="false"
    chooseLabel="Wybierz plik"
    :multiple="false"
    :accept="props.acceptableFiles"
    :maxFileSize="props.maxFileSize"
    :fileLimit="1"
    :invalidFileTypeMessage="props.invalidFileTypeMessage"
    @select="
      (event) => {
        if (!event.files || event.files.length === 0) return;

        isFileChosen = true;
        emit('file-selected', event.files[0]);
      }
    "
    @error="
      () => {
        isFileChosen = false;
      }
    "
  >
    <template #empty>
      <span class="font-semibold">{{ props.dragAndDropMessage }}</span>
    </template>

    <!-- File icon and name -->
    <template #content="{ files, removeFileCallback }">
      <div
        v-for="(file, index) in files"
        :key="file.name"
        class="flex justify-between items-center w-full"
      >
        <div class="flex items-center gap-2">
          <i :class="'pi ' + props.fileIcon + ' text-primary'"></i>
          <span class="font-medium">{{ file.name }}</span>
        </div>

        <!-- Status + Remove file button -->
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">Gotowy</span>
          <Button
            icon="pi pi-times"
            severity="danger"
            rounded
            text
            @click="
              () => {
                removeFileCallback(index);
                isFileChosen = false;
                emit('file-removed');
              }
            "
          />
        </div>
      </div>
    </template>
  </FileUpload>
</template>
