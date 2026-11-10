<script setup lang="ts">
import { ref, watch } from "vue";
import type { MonthlyProfitItem } from "../../../lib/types/cashflow";

import YearChoiceTopBar from "../components/YearChoiceTopBar.vue";
import MonthChoiceTopBar from "../components/MonthChoiceTopBar.vue";
import InvoicesSummaryList from "../components/InvoicesSummaryList.vue";
import InvoicesSummaryBar from "../components/InvoicesSummaryBar.vue";
import CasflowMonthlyChart from "../components/CasflowMonthlyChart.vue";

const selectedYear = ref(new Date().getFullYear());
const selectedMonth = ref<number | null>(new Date().getMonth() + 1);
const selectedMonthProfit = ref<number | undefined>(undefined);
const monthlyProfitList = ref<MonthlyProfitItem[]>([]);
const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

watch([selectedYear, selectedMonth], ([year, month]) => {
  if (year === currentYear && month !== null && month > currentMonth) {
    selectedMonth.value = currentMonth;
  }
});

function onMonthSelect(monthNumber: number | null) {
  selectedMonth.value = monthNumber;
  selectedMonthProfit.value = monthlyProfitList.value.find(
    (item) => item.month_number === monthNumber,
  )?.net_profit;
}

function onYearSelect(year: number) {
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
      @fetch:monthlyProfitList="
        (data) => {
          monthlyProfitList = data;
          onMonthSelect(selectedMonth);
        }
      "
    />

    <div class="p-div-grey mt-4 gap-4 flex min-h-0 flex-1 flex-col justify-start overflow-y-auto">
      <InvoicesSummaryBar
        :selected-year="selectedYear"
        :selected-month="selectedMonth"
        :monthly-profit="selectedMonthProfit"
      />
      <div class="flex shrink-0 items-start gap-4">
        <InvoicesSummaryList
          :selected-year="selectedYear"
          :selected-month="selectedMonth"
          :type="'sales'"
          :month-sales="
            monthlyProfitList.find((item) => item.month_number === selectedMonth)?.net_sales
          "
          :previus-month-sales="
            monthlyProfitList.find((item) => item.month_number === selectedMonth - 1)?.net_sales
          "
          :month-costs="
            monthlyProfitList.find((item) => item.month_number === selectedMonth)?.net_costs
          "
          :previous-month-costs="
            monthlyProfitList.find((item) => item.month_number === selectedMonth - 1)?.net_costs
          "
        />
        <InvoicesSummaryList
          :selected-year="selectedYear"
          :selected-month="selectedMonth"
          :type="'purchases'"
          :month-costs="
            monthlyProfitList.find((item) => item.month_number === selectedMonth)?.net_costs
          "
          :previous-month-costs="
            monthlyProfitList.find((item) => item.month_number === selectedMonth - 1)?.net_costs
          "
          :month-sales="
            monthlyProfitList.find((item) => item.month_number === selectedMonth)?.net_sales
          "
          :previus-month-sales="
            monthlyProfitList.find((item) => item.month_number === selectedMonth - 1)?.net_sales
          "
        />
      </div>
      <CasflowMonthlyChart :selected-year="selectedYear" :selected-month="selectedMonth" />
    </div>
  </div>
</template>
