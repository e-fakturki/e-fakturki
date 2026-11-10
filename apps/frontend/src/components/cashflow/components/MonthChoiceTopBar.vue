<script setup lang="ts">
import { Button, useToast } from "primevue";
import { useMutation } from "@tanstack/vue-query";
import { ref, watch } from "vue";

import { monthsDictionary } from "../../../lib/constants.ts";
import MonthTopBarSegment from "./MonthTopBarSegment.vue";
import { getMonthlyProfitList } from "../../../lib/services/cashflowDashboardService.ts";
import type { MonthlyProfitItem } from "../../../lib/types/cashflow";
import { useCurrentUserStore } from "../../../stores/currentUserStore.ts";

const props = defineProps<{
  selectedYear: number;
  selectedMonth: number | null;
}>();

const emit = defineEmits<{
  (e: "update:selectedMonth", monthNumber: number | null): void;
  (e: "fetch:monthlyProfitList", monthlyProfitList: MonthlyProfitItem[]): void;
}>();

const toast = useToast();
const currentUserStore = useCurrentUserStore();

const monthNumbers = Object.keys(monthsDictionary).map(Number);
const monthlyProfits = ref<MonthlyProfitItem[]>([]);

function selectMonth(monthNumber: number | null) {
  emit("update:selectedMonth", monthNumber);

  if (monthNumber === null) {
    toast.add({
      severity: "warn",
      summary: "Brak danych dla wybranego miesiąca, dodaj dane lub pobierz faktury z KSeF",
      life: 5000,
    });
  }
}

const getMonthlyProfitListMutation = useMutation({
  mutationFn: async () => {
    const companyId = currentUserStore.getCompanyId;
    return await getMonthlyProfitList(companyId!, props.selectedYear);
  },

  onSuccess: (data) => {
    monthlyProfits.value = data;
    emit("fetch:monthlyProfitList", data);
    selectMonth(props.selectedMonth);
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

watch(
  () => props.selectedYear,
  () => {
    getMonthlyProfitListMutation.mutate();
  },
  { immediate: true },
);
</script>

<template>
  <div class="flex justify-between items-center w-full pt-4 gap-4">
    <template v-for="monthNumber in monthNumbers" :key="monthNumber">
      <MonthTopBarSegment
        :month-number="monthNumber"
        :selected-year="props.selectedYear"
        :selected-month="props.selectedMonth"
        :profit="monthlyProfits.find((item) => item.month_number === monthNumber)?.net_profit"
        @update:selected-month="selectMonth($event)"
      />
    </template>
    <Button
      class="month-segment flex flex-1 items-center justify-center h-20"
      :class="{
        'font-semibold': props.selectedMonth === null,
        'month-segment-selected': props.selectedMonth === null,
      }"
      outlined
      @click="selectMonth(null)"
    >
      {{ `Cały rok ${props.selectedYear}` }}
    </Button>
  </div>
</template>
