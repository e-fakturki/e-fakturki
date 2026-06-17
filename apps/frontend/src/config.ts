import Aura from "@primeuix/themes/aura";
import { definePreset } from "@primeuix/themes";

export const apiConfig = {
  apiBaseUrl: "http://localhost:8000/api",

  endpoints: {
    ksef: "/ksef",
    auth: "/auth",
    companies: "/companies",
    invoices: "/invoices",
    users: "/users",
    products: "/products",
    categories: "/categories",
  },

  // Other application settings
  defaultPageSize: 10,
  tokenStorageKey: "user",
};

export const customPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: "{sky.50}",
      100: "{sky.100}",
      200: "{sky.200}",
      300: "{sky.300}",
      400: "{sky.400}",
      500: "{sky.500}",
      600: "{sky.600}",
      700: "{sky.700}",
      800: "{sky.800}",
      900: "{sky.900}",
      950: "{sky.950}",
    },
  },
});

export const primeVueConfig = {
  theme: {
    preset: customPreset,
    options: {
      prefix: "prime",
      darkModeSelector: ".prime-dark-mode",
      //   darkModeSelector: "system",
    },
  },
  ripple: true,
  inputVariant: "filled",
  locale: {
    dayNames: ["niedziela", "poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota"],
    dayNamesMin: ["ndz", "pon", "wt", "śr", "czw", "pt", "sob"],
    monthNames: [
      "styczeń",
      "luty",
      "marzec",
      "kwiecień",
      "maj",
      "czerwiec",
      "lipiec",
      "sierpień",
      "wrzesień",
      "październik",
      "listopad",
      "grudzień",
    ],
    monthNamesShort: [
      "sty",
      "lut",
      "mar",
      "kwi",
      "maj",
      "cze",
      "lip",
      "sie",
      "wrz",
      "paź",
      "lis",
      "gru",
    ],
    today: "Dziś",
    clear: "Wyczyść",
    noAvailableOptions: "Brak opcji do wyboru",
  },
};
