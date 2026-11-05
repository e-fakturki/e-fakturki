<script setup lang="ts">
import { Button, useToast } from "primevue";
import { useMutation } from "@tanstack/vue-query";
import { onMounted, ref } from "vue";

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
}>();

const toast = useToast();
const currentUserStore = useCurrentUserStore();

const monthlyProfits = ref<MonthlyProfitItem[]>([]);

const getMonthlyProfitListMutation = useMutation({
  mutationFn: async () => {
    const companyId = currentUserStore.getCompanyId;
    return await getMonthlyProfitList(companyId!, props.selectedYear);
  },

  onSuccess: (data) => {
    monthlyProfits.value = data;
    console.log(monthlyProfits);
  },

  onError: (error) => {
    toast.add({ severity: "error", summary: error.response?.data?.detail, life: 5000 });
  },
});

const monthNumbers = Object.keys(monthsDictionary).map(Number);

onMounted(() => {
  getMonthlyProfitListMutation.mutate();
});
</script>

<template>
  <div class="flex justify-between items-center w-full pt-4 gap-4">
    <template v-for="monthNumber in monthNumbers" :key="monthNumber">
      <MonthTopBarSegment
        :monthNumber="monthNumber"
        :selectedYear="props.selectedYear"
        :selectedMonth="props.selectedMonth"
        :profit="monthlyProfits.find((item) => item.month_number === monthNumber)?.net_profit"
        @update:selectedMonth="emit('update:selectedMonth', $event)"
      />
    </template>
    <Button
      class="month-segment flex flex-1 items-center justify-center h-20"
      :class="{
        'font-semibold': props.selectedMonth === null,
        'month-segment-selected': props.selectedMonth === null,
      }"
      outlined
      @click="emit('update:selectedMonth', null)"
    >
      {{ `Cały rok ${props.selectedYear}` }}
    </Button>
  </div>
</template>
