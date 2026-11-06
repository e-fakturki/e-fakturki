<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import AddKsefCredentials from "../components/dialogs/AddKsefCredentials.vue";
import LoginDialog from "../components/dialogs/LoginDialog.vue";
import CompanyForm from "../components/inputs/CompanyForm.vue";

const router = useRouter();

const showLoginForm = ref(true);
const showCompanyForm = ref(false);
const showKsefCredsForm = ref(false);

function onLogin() {
  showLoginForm.value = false;
  router.push("/new-invoice");
}

function onRegister() {
  showLoginForm.value = false;
  showCompanyForm.value = true;
}

function onAddCompany() {
  showCompanyForm.value = false;
  showKsefCredsForm.value = true;
}

function onKsefAuthorize() {
  showKsefCredsForm.value = false;
  router.push("/new-invoice");
}
</script>

<template>
  <div>
    <LoginDialog
      v-model:visible="showLoginForm"
      @login-success="onLogin"
      @register-success="onRegister"
    />
    <CompanyForm
      v-model:visible="showCompanyForm"
      create-or-update="create"
      :user-company="true"
      :company-info="null"
      :loading="false"
      @success="onAddCompany"
      @cancel="null"
    />
    <AddKsefCredentials v-model:visible="showKsefCredsForm" @success="onKsefAuthorize" />
  </div>
</template>
