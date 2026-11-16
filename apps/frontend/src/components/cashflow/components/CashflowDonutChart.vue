<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { Doughnut } from "vue-chartjs";
import { Chart as ChartJS, ArcElement, Title, Tooltip, Legend, type ChartOptions } from "chart.js";
import { schemeSet3 } from "d3-scale-chromatic";

import type { MonthlyProfitItem } from "../../../lib/types/cashflow";
import { formatPLN } from "../../../lib/utils";

import productSales from "../../../assets/mock_donut1";

const props = defineProps<{
  selectedYear: number;
  selectedMonth: number | null;
  title: string;
  monthlyProfitList: MonthlyProfitItem[];
}>();

// WHAT TO DO IF TOO MUCH DATA????? MORE THAN 30??? VERTICAL BAR CHART ?????

const getChartColors = () => {
  const styles = getComputedStyle(document.documentElement);
  return {
    text: styles.getPropertyValue("--chart-text").trim(),
    grid: styles.getPropertyValue("--chart-grid").trim(),
    tooltipBackground: styles.getPropertyValue("--chart-tooltip-bg").trim(),
    donutChartBorder: styles.getPropertyValue("--donut-chart-border").trim(),
  };
};
const chartColors = ref(getChartColors());
let themeObserver: MutationObserver | undefined;
const salesLabels = Object.keys(productSales.sales_distribution);

const data = ref({
  labels: salesLabels,
  datasets: [
    {
      backgroundColor: salesLabels.map((_, index) => schemeSet3[index % schemeSet3.length]),
      borderColor: chartColors.value.donutChartBorder,
      borderWidth: 2,
      hoverOffset: 8,
      pointRadius: 0,
      pointHoverRadius: 10,
      data: Object.values(productSales.sales_distribution),
    },
  ],
});

onMounted(() => {
  themeObserver = new MutationObserver(() => {
    chartColors.value = getChartColors();
  });
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });
});

onUnmounted(() => themeObserver?.disconnect());

// watch(
//   [() => props.selectedYear, () => props.selectedMonth, () => props.monthlyProfitList],
//   () => {
//     monthCount.value = props.selectedMonth ?? 12;
//     const profitByMonth = new Map(props.monthlyProfitList.map((item) => [item.month_number, item]));

//     data.value = {
//       labels: Object.values(monthsDictionary).slice(0, monthCount.value),
//       datasets: [
//         {
//           label: "Przychód netto",
//           backgroundColor: "rgba(121, 248, 121, 0.2)",
//           borderColor: "#79f879",
//           pointRadius: 0,
//           pointHoverRadius: 10,
//           data: Array.from(
//             { length: monthCount.value },
//             (_, index) => profitByMonth.get(index + 1)?.net_sales ?? 0,
//           ),
//         },
//         {
//           label: "Koszty netto",
//           backgroundColor: "rgba(248, 121, 121, 0.2)",
//           borderColor: "#f87979",
//           pointRadius: 0,
//           pointHoverRadius: 10,
//           data: Array.from(
//             { length: monthCount.value },
//             (_, index) => profitByMonth.get(index + 1)?.net_costs ?? 0,
//           ),
//         },
//       ],
//     };
//   },
//   { immediate: true },
// );

const options = computed<ChartOptions<"doughnut">>(() => ({
  responsive: true,
  maintainAspectRatio: false,

  interaction: {
    mode: "nearest",
    intersect: true,
  },
  plugins: {
    legend: {
      position: "bottom",
      labels: {
        font: { size: 14 },
        color: chartColors.value.text,
      },
    },
    tooltip: {
      backgroundColor: chartColors.value.tooltipBackground,
      titleFont: { size: 14 },
      titleColor: chartColors.value.text,
      bodyFont: { size: 14 },
      bodyColor: chartColors.value.text,
      footerFont: { size: 14 },
      footerColor: chartColors.value.text,
      callbacks: {
        label(context) {
          const value = context.parsed;
          const formattedValue = Number.isFinite(value) ? formatPLN(value) : "brak danych";
          return `${context.label}: ${formattedValue}`;
        },
      },
    },
  },
}));

ChartJS.register(ArcElement, Title, Tooltip, Legend);
</script>

<template>
  <div class="flex min-w-0 flex-col p-div-white relative h-[32rem] w-full gap-4">
    <h1 class="text-xl font-bold">{{ title }}</h1>
    <Doughnut :data="data" :options="options" />
  </div>
</template>
