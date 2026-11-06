import "./style.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router/router";
import { createPinia } from "pinia";
import { ToastService } from "primevue";
import { VueQueryPlugin } from "@tanstack/vue-query";
import PrimeVue from "primevue/config";
import { primeVueConfig } from "./config";
import Tooltip from "primevue/tooltip";

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);

app.use(router);

app.use(ToastService);

app.use(VueQueryPlugin);

app.use(PrimeVue, primeVueConfig);
app.directive("tooltip", Tooltip);

app.mount("#app");
