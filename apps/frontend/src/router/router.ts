import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import NewInvoiceView from "../views/NewInvoiceView.vue";
import SalesView from "../views/SalesView.vue";
import PurchasesView from "../views/PurchasesView.vue";
import ProductsView from "../views/ProductsView.vue";
import CompaniesView from "../views/CompaniesView.vue";
import SettingsView from "../views/SettingsView.vue";
import { useCurrentUserStore } from "../stores/currentUserStore";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: "/login",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { requiresAuth: false },
    },
    {
      path: "/sales",
      name: "sales",
      component: SalesView,
      meta: { requiresAuth: true },
    },
    {
      path: "/new-invoice",
      name: "new-invoice",
      component: NewInvoiceView,
      meta: { requiresAuth: true },
    },
    {
      path: "/purchases",
      name: "purchases",
      component: PurchasesView,
      meta: { requiresAuth: true },
    },
    {
      path: "/products",
      name: "products",
      component: ProductsView,
      meta: { requiresAuth: true },
    },
    {
      path: "/companies",
      name: "companies",
      component: CompaniesView,
      meta: { requiresAuth: true },
    },
    {
      path: "/settings",
      name: "settings",
      component: SettingsView,
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach(async (to) => {
  const currentUserStore = useCurrentUserStore();
  const token = currentUserStore.getToken;

  if (to.meta.requiresAuth && !token) {
    return { name: "login" };
  }
  if (to.name === "login" && token) {
    return { name: "new-invoice" };
  }
});

export default router;
