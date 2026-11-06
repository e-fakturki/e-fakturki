<script setup lang="ts">
import LeftMenu from "./components/LeftMenu.vue";
import TopBar from "./components/TopBar.vue";
import { Toast } from "primevue";
</script>

<template>
  <div class="app-container">
    <TopBar />
    <div class="main-container">
      <LeftMenu />
      <!-- Main content area -->
      <div class="content-area">
        <Toast />
        <RouterView />
      </div>
    </div>
  </div>
</template>
