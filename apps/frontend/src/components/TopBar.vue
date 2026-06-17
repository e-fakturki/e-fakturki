<script setup lang="ts">
import { computed } from "vue";
import { ref } from "vue";
import { Toolbar, Select, Button, Popover, useToast, Divider } from "primevue";

import AppLogo from "./AppLogo.vue";
import { useCurrentUserStore } from "../stores/currentUserStore";
import { userLogout } from "../lib/services/authService";
import router from "../router/router";

const currentUserStore = useCurrentUserStore();
const toast = useToast();

const userPopup = ref();
const toggleUserPopup = (event: any) => {
  userPopup.value.toggle(event);
};

function logout() {
  userLogout();
  userPopup.value.hide();
  router.push("/login");
  setTimeout(() => {
    toast.add({ severity: "info", summary: "Poprawnie wylogowano", life: 3000 });
  }, 100);
}

const companyName = computed(() => currentUserStore.getCompanyName);
const userName = computed(() => currentUserStore.getFullName);
</script>

<template>
  <Toolbar>
    <template #start>
      <AppLogo />
    </template>

    <template #end>
      <div class="flex items-center gap-4">
        <Select
          :placeholder="companyName ?? 'Wybierz firmę'"
          emptyMessage="Brak opcji do wyboru"
          disabled
        />
        <p>{{ userName ? userName : "Zaloguj się" }}</p>
        <Button icon="pi pi-user" raised rounded @click="toggleUserPopup" />
      </div>
    </template>
  </Toolbar>

  <!-- user popup -->
  <Popover ref="userPopup">
    <div class="flex flex-col w-40">
      <div class="flex flex-col">
        <span>Zalogowano jako:</span>
        <span class="font-semibold">{{ currentUserStore.getFullName }}</span>
      </div>
      <Divider />
      <Button icon="pi pi-on-off-button" label="Wyloguj" raised @click="logout"></Button>
    </div>
  </Popover>
</template>
