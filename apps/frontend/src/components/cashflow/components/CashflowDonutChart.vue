<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { Doughnut } from "vue-chartjs";
import { Chart as ChartJS, ArcElement, Title, Tooltip, Legend, type ChartOptions } from "chart.js";
import { useMutation } from "@tanstack/vue-query";
import { useToast } from "primevue";
import { schemeSet3 } from "d3-scale-chromatic";

import type { CashflowDonutChartType } from "../../../lib/types/cashflow";
import { getCashflowPerContractorDistribution } from "../../../lib/services/cashflowDashboardService";
import { formatPLN, trimLabels } from "../../../lib/utils";
import { useCurrentUserStore } from "../../../stores/currentUserStore";

const props = defineProps<{
  selectedYear: number;
  selectedMonth: number | null;
  title: string;
  type: CashflowDonutChartType;
}>();

const toast = useToast();
const currentUserStore = useCurrentUserStore();

const getChartColors = () => {
  const styles = getComputedStyle(document.documentElement);
  return {
    text: styles.getPropertyValue("--chart-text").trim(),
    grid: styles.getPropertyValue("--chart-grid").trim(),
    tooltipText: styles.getPropertyValue("--chart-tooltip-text").trim(),
    tooltipBackground: styles.getPropertyValue("--chart-tooltip-bg").trim(),
    donutChartBorder: styles.getPropertyValue("--donut-chart-border").trim(),
  };
};
const chartColors = ref(getChartColors());
let themeObserver: MutationObserver | undefined;
const LABEL_MAX_LENGTH = 72;
const salesLabels = ref<string[]>([]);
const salesData = ref<number[]>([]);
const legendItems = ref<{ label: string; value: number; color: string }[]>([]);
const data = ref({
  labels: [] as string[],
  datasets: [
    {
      backgroundColor: [] as string[],
      labels: [] as string[],
      borderColor: chartColors.value.donutChartBorder,
      borderWidth: 2,
      hoverOffset: 8,
      pointRadius: 0,
      pointHoverRadius: 10,
      data: [] as number[],
    },
  ],
});

function wrapTooltipLabel(label: string, maxLength = 22) {
  const lines: string[] = [];
  let line = "";

  for (const word of label.split(/\s+/).filter(Boolean)) {
    if (line && line.length + word.length + 1 > maxLength) {
      lines.push(line);
      line = word;
    } else {
      line = line ? `${line} ${word}` : word;
    }
  }

  if (line) lines.push(line);
  return lines;
}

const getDistributionData = useMutation({
  mutationFn: async () => {
    const companyId = currentUserStore.getCompanyId;
    return await getCashflowPerContractorDistribution(
      companyId!,
      props.selectedYear,
      props.selectedMonth,
      props.type,
    );
  },

  onSuccess: (items) => {
    salesLabels.value = items.map(
      (item) => trimLabels(item.contractor_name, LABEL_MAX_LENGTH) ?? "Nieznany kontrahent",
    );
    salesData.value = items.map((item) => item.net_cashflow);
    legendItems.value = salesLabels.value.map((label, index) => ({
      label,
      value: salesData.value[index] ?? 0,
      color: schemeSet3[index % schemeSet3.length] ?? "#b8cdbb",
    }));
    data.value = {
      labels: salesLabels.value,
      datasets: [
        {
          backgroundColor: legendItems.value.map((item) => item.color),
          labels: salesLabels.value.map((label) => trimLabels(label, LABEL_MAX_LENGTH)),
          borderColor: chartColors.value.donutChartBorder,
          borderWidth: 2,
          hoverOffset: 8,
          pointRadius: 0,
          pointHoverRadius: 10,
          data: salesData.value,
        },
      ],
    };
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

onMounted(() => {
  themeObserver = new MutationObserver(() => {
    chartColors.value = getChartColors();
    data.value = {
      ...data.value,
      datasets: data.value.datasets.map((dataset) => ({
        ...dataset,
        borderColor: chartColors.value.donutChartBorder,
      })),
    };
  });
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });
});

onUnmounted(() => themeObserver?.disconnect());

watch(
  [() => props.selectedYear, () => props.selectedMonth],
  () => {
    getDistributionData.mutate();
  },
  { immediate: true },
);

const options = computed<ChartOptions<"doughnut">>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: "nearest",
    intersect: true,
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      maxWidth: 180,
      caretPadding: 8,
      padding: 8,
      backgroundColor: chartColors.value.tooltipBackground,
      titleFont: { size: 14 },
      titleColor: chartColors.value.tooltipText,
      bodyFont: { size: 14 },
      bodyColor: chartColors.value.tooltipText,
      footerFont: { size: 14 },
      footerColor: chartColors.value.text,
      callbacks: {
        title: () => "",
        label(context) {
          const value = context.parsed;
          const formattedValue = Number.isFinite(value) ? formatPLN(value) : "brak danych";
          return [...wrapTooltipLabel(context.label), formattedValue];
        },
      },
    },
  },
}));

ChartJS.register(ArcElement, Title, Tooltip, Legend);
</script>

<template>
  <div class="relative flex h-[32rem] min-w-0 w-full flex-col gap-3 p-div-white">
    <h1 class="shrink-0 text-xl font-bold">{{ title }}</h1>
    <div class="h-80 w-full max-w-80 shrink-0 self-center">
      <Doughnut :data="data" :options="options" />
    </div>
    <ul class="min-h-0 flex-1 space-y-1 overflow-y-auto pr-2" :aria-label="`${title} legenda`">
      <li
        v-for="(item, index) in legendItems"
        :key="`${item.label}-${index}`"
        class="flex min-w-0 items-center gap-2 text-sm"
      >
        <span class="h-3 w-3 shrink-0 rounded-sm" :style="{ backgroundColor: item.color }"></span>
        <span class="min-w-0 flex-1 truncate" :title="item.label">{{ item.label }}</span>
        <span class="shrink-0 tabular-nums">{{ formatPLN(item.value) }}</span>
      </li>
    </ul>
  </div>
</template>
