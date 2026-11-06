<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  type ChartOptions,
} from "chart.js";
import { formatPLN } from "../../../lib/utils";

import { monthsDictionary } from "../../../lib/constants.ts";

const props = defineProps<{
  selectedYear: number;
  selectedMonth: number | null;
}>();

const getChartColors = () => {
  const styles = getComputedStyle(document.documentElement);
  return {
    text: styles.getPropertyValue("--chart-text").trim(),
    grid: styles.getPropertyValue("--chart-grid").trim(),
    tooltipBackground: styles.getPropertyValue("--chart-tooltip-bg").trim(),
  };
};
const chartColors = ref(getChartColors());
let themeObserver: MutationObserver | undefined;

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

// Randomly generated cashflow values for demonstration purposes
const monthCount = props.selectedMonth ?? 12;
const cashflows = Array.from({ length: monthCount }, () => Math.floor(Math.random() * 1000));
const costs = Array.from({ length: monthCount }, (_, i) =>
  Math.floor(cashflows[i]! * (0.9 + Math.random() * 0.2)),
);

const data = {
  labels: Object.values(monthsDictionary).slice(0, monthCount),
  datasets: [
    {
      label: "Przychód netto",
      backgroundColor: "rgba(121, 248, 121, 0.2)",
      borderColor: "#79f879",
      pointRadius: 0,
      pointHoverRadius: 10,
      data: cashflows,
    },
    {
      label: "Koszty netto",
      backgroundColor: "rgba(248, 121, 121, 0.2)",
      borderColor: "#f87979",
      pointRadius: 0,
      pointHoverRadius: 10,
      data: costs,
    },
  ],
};

const options = computed<ChartOptions<"line">>(() => ({
  responsive: true,
  maintainAspectRatio: false,

  scales: {
    x: {
      ticks: {
        font: { size: 14 },
        color: chartColors.value.text,
      },
      grid: {
        color: chartColors.value.grid,
      },
    },
    y: {
      ticks: {
        font: { size: 14 },
        color: chartColors.value.text,
      },
      grid: {
        color: chartColors.value.grid,
      },
    },
  },
  interaction: {
    mode: "index",
    intersect: false,
  },
  plugins: {
    legend: {
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
          const value = context.parsed.y;
          const formattedValue = value === null ? "brak danych" : formatPLN(value);
          return `${context.dataset.label}: ${formattedValue}`;
        },
      },
    },
  },
}));

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);
</script>

<template>
  <div class="p-div-white relative h-[32rem] w-full shrink-0">
    <Line :data="data" :options="options" />
  </div>
</template>
