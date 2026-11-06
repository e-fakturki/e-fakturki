<script setup lang="ts">
import { formatPLN } from "../../../lib/utils";

const props = defineProps<{
  selectedYear: number;
  selectedMonth: number | null;
}>();

// Randomly generated cashflow values for demonstration purposes
const profit = Math.floor(Math.random() * 1000);
const invoiceAmount = Math.floor(Math.random() * 50);
const averageInvoice = Math.floor(Math.random() * 500);
const newClients = Math.floor(Math.random() * 5); // Względem poprzedniego miesiąca ? Czy calej bazy klientów?
const lostClients = Math.floor(Math.random() * 5); // Względem poprzedniego miesiąca ? Czy calej bazy klientów?
// dla obu rodzajów faktur sytuacja w której status platnosci wewnetrzy w aplikacji jest niezaplacone a termin platnosci minal
const invoicesNotPayed = Math.floor(Math.random() * 20);
const costInvoicesNotPayed = Math.floor(Math.random() * 20);
</script>

<template>
  <div class="p-div-white flex flex-col gap-2">
    <!-- INVOICES SUMMARY -->
    <div class="flex flex-col gap-4 justify-start">
      <h1 class="text-xl font-bold">Potencjalny dochód netto {{ formatPLN(profit) }}</h1>
      <div class="flex w-full justify-between">
        <div class="flex flex-col gap-2">
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Ilość sprzedaży</h3>
            <h1 class="text-xl font-bold">
              {{ invoiceAmount }}
            </h1>
          </div>
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Ilość kosztów</h3>
            <h1 class="text-xl font-bold">
              {{ invoiceAmount }}
            </h1>
          </div>
        </div>
        <div class="flex flex-col gap-2">
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Średnia wartość netto sprzedaży</h3>
            <h1 class="text-xl font-bold">
              {{ formatPLN(averageInvoice) }}
            </h1>
          </div>
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Średnia wartość netto kosztu</h3>
            <h1 class="text-xl font-bold">
              {{ formatPLN(averageInvoice) }}
            </h1>
          </div>
        </div>
        <div class="flex flex-col gap-2">
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Nowi klienci</h3>
            <h1 class="text-xl font-bold">
              {{ newClients }}
            </h1>
          </div>
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Nieaktywni klienci (względem ostatniego miesiąca)</h3>
            <h1 class="text-xl font-bold">
              {{ lostClients }}
            </h1>
          </div>
        </div>
        <div class="flex flex-col gap-2">
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Zaległe płatności od klientów</h3>
            <h1 class="text-xl font-bold">
              {{ invoicesNotPayed }}
            </h1>
          </div>
          <div class="flex flex-col gap-1">
            <h3 class="p-h3">Zaległe płatności dla dostawców</h3>
            <h1 class="text-xl font-bold">
              {{ costInvoicesNotPayed }}
            </h1>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
