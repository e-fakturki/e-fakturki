export const monthsDictionary = {
  1: "Styczeń",
  2: "Luty",
  3: "Marzec",
  4: "Kwiecień",
  5: "Maj",
  6: "Czerwiec",
  7: "Lipiec",
  8: "Sierpień",
  9: "Wrzesień",
  10: "Październik",
  11: "Listopad",
  12: "Grudzień",
};

export const incomeTypes = {
  invoice: {
    label: "Faktura",
    description: "Faktury sprzedażowe (domyślnie pobierane z KSeF)",
  },
  bill: {
    label: "Sprzedaż detaliczna",
    description: "Dane sprzedażowe z paragonów i kas fiskalnych (mogą być pojedyncze lub zbiorowe)",
  },
  other: {
    label: "Inne",
    description: "Inne źródła przychodów (np. dotacje, dywidendy)",
  },
};

export const costTypes = {
  invoice: {
    label: "Faktura",
    description: "Faktury kosztowe (domyślnie pobierane z KSeF)",
  },
  operational: {
    label: "Koszty operacyjne",
    description:
      "Koszty związane z bieżącą działalnością operacyjną (przykładowo: wynajem biura, media, paliwo)",
  },
  salary: {
    label: "Wynagrodzenia",
    description: "Koszty związane z wynagrodzeniami pracowników",
  },
  tax: {
    label: "Podatki i składki",
    description: "Koszty związane z podatkami i składkami ZUS",
  },
  insurance: {
    label: "Ubezpieczenia",
    description: "Koszty związane z ubezpieczeniami",
  },
  lease: {
    label: "Leasing",
    description: "Koszty związane z leasingiem",
  },
  other: {
    label: "Inne",
    description: "Inne koszty (nie sklasyfikowane w powyższych kategoriach)",
  },
};
