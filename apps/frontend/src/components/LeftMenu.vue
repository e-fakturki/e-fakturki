<script setup lang="ts">
import { ref } from "vue";
import { Menu, Badge } from "primevue";
import { toggleDarkMode } from "../lib/utils";
import { useInvoicesStore } from "../stores/invoicesStore";

const invoicesStore = useInvoicesStore();

const items = ref([
  {
    label: "Faktury",
    items: [
      {
        label: "Nowa Faktura",
        icon: "pi pi-plus",
        route: "/new-invoice",
        disabled: false,
      },
      {
        label: "Sprzedaż",
        icon: "pi pi-shop",
        route: "/sales",
        disabled: false,
      },
      {
        label: "Zakup",
        icon: "pi pi-shopping-cart",
        route: "/purchases",
        disabled: false,
      },
    ],
  },
  {
    label: "Firma",
    items: [
      {
        label: "Produkty",
        icon: "pi pi-box",
        route: "/products",
        disabled: false,
      },
      {
        label: "Firmy",
        icon: "pi pi-user",
        route: "/companies",
        disabled: false,
      },
    ],
  },
  {
    label: "Aplikacja",
    items: [
      {
        label: "Tryb",
        icon: "pi pi-sun",
        command: toggleDarkMode,
      },
      {
        label: "Ustawienia",
        icon: "pi pi-cog",
        route: "/settings",
        disabled: true,
      },
    ],
  },
]);
</script>

<template>
  <div class="card flex h-full">
    <Menu :model="items" class="w-full md:w-60 h-full">
      <template #item="{ item, props }">
        <router-link
          v-if="item.route"
          v-slot="{ href, navigate, isActive }"
          :to="item.route"
          custom
          :disabled="item.disabled"
        >
          <a
            v-ripple
            :href="href"
            v-bind="props.action"
            @click="navigate"
            :class="['flex items-center w-full', { 'bg-primary-100 font-semibold': isActive }]"
          >
            <span :class="item.icon" />
            <span class="ml-2">{{ item.label }}</span>
            <Badge
              v-if="
                (item.route === '/sales' && invoicesStore.getSalesInvoicesCount > 0) ||
                (item.route === '/purchases' && invoicesStore.getPurchaseInvoicesCount > 0)
              "
              class="ml-auto rounded-xs"
              :value="
                item.route === '/sales'
                  ? invoicesStore.getSalesInvoicesCountStr
                  : invoicesStore.getPurchaseInvoicesCountStr
              "
            />
          </a>
        </router-link>
        <a v-else v-ripple :href="item.url" :target="item.target" v-bind="props.action">
          <span :class="item.icon" />
          <span class="ml-2">{{ item.label }}</span>
        </a>
      </template>
    </Menu>
  </div>
</template>
