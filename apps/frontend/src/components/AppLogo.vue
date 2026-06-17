<script setup lang="ts">
import { ref } from "vue";

const appName = ref("e-fakturki");
const appVer = ref("v0.1.0");
</script>

<template>
  <div class="flex items-baseline gap-2">
    <div class="flex text-3xl font-bold text-primary">
      {{ appName }}
    </div>
    <div class="flex font-semibold text-gray-500">
      {{ appVer }}
    </div>
  </div>
</template>
