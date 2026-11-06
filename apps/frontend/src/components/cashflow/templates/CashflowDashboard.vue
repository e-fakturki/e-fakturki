<script setup lang="ts">
import { ref, watch } from "vue";

import { useToast } from "primevue";
import { useMutation } from "@tanstack/vue-query";
import Toolbar from "primevue/toolbar";

import YearChoiceTopBar from "../components/YearChoiceTopBar.vue";
import MonthChoiceTopBar from "../components/MonthChoiceTopBar.vue";
import InvoicesSummaryList from "../components/InvoicesSummaryList.vue";
import InvoicesSummaryBar from "../components/InvoicesSummaryBar.vue";
import CasflowMonthlyChart from "../components/CasflowMonthlyChart.vue";

const toast = useToast();

const selectedYear = ref(new Date().getFullYear());
const selectedMonth = ref<number | null>(new Date().getMonth() + 1);
const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

watch([selectedYear, selectedMonth], ([year, month]) => {
  if (year === currentYear && month !== null && month > currentMonth) {
    selectedMonth.value = currentMonth;
  }
});

function onMonthSelect(monthNumber: number | null) {
  console.log("Month selected:", monthNumber);
  selectedMonth.value = monthNumber;
}

function onYearSelect(year: number) {
  console.log("Year selected:", year);
  selectedYear.value = year;
}
</script>

<template>
  <div class="flex h-full min-h-0 flex-col">
    <YearChoiceTopBar :selected-year="selectedYear" @update:selected-year="onYearSelect" />
    <MonthChoiceTopBar
      :selected-year="selectedYear"
      :selected-month="selectedMonth"
      @update:selected-month="onMonthSelect"
    />

    <div class="p-div-grey mt-4 gap-4 flex min-h-0 flex-1 flex-col justify-start overflow-y-auto">
      <InvoicesSummaryBar :selected-year="selectedYear" :selected-month="selectedMonth" />
      <div class="flex shrink-0 items-start gap-4">
        <InvoicesSummaryList
          :selected-year="selectedYear"
          :selected-month="selectedMonth"
          :type="'sales'"
        />
        <InvoicesSummaryList
          :selected-year="selectedYear"
          :selected-month="selectedMonth"
          :type="'purchases'"
        />
      </div>
      <CasflowMonthlyChart :selected-year="selectedYear" :selected-month="selectedMonth" />
    </div>
  </div>
</template>
