<script setup lang="ts">
import { computed } from "vue";
import { monthsDictionary } from "../../../lib/constants";
import Button from "primevue/button";
import { formatPLN } from "../../../lib/utils";

const props = defineProps<{
  monthNumber: number;
  selectedYear: number;
  selectedMonth: number | null;
  profit: number | null | undefined;
}>();

const emit = defineEmits<{
  (e: "update:selectedMonth", monthNumber: number): void;
}>();

// Random profit for demonstration purposes
// const profit = Math.floor(Math.random() * (5432 + 1389 + 1)) - 1389;

const disabled = computed(
  () =>
    props.selectedYear === new Date().getFullYear() &&
    props.monthNumber > new Date().getMonth() + 1,
);

function handleSelectMonth() {
  if (!disabled.value) {
    // Emit an event to the parent component to update the selected month
    emit("update:selectedMonth", props.monthNumber);
  }
}
</script>

<template>
  <Button
    class="month-segment flex flex-1 items-center justify-center h-20"
    :class="{
      'font-semibold': props.monthNumber === props.selectedMonth,
      'month-segment-selected': props.monthNumber === props.selectedMonth,
    }"
    outlined
    :disabled="disabled"
    :aria-pressed="props.selectedMonth === props.monthNumber"
    @click="handleSelectMonth"
  >
    <div class="flex flex-col items-center">
      <div>{{ monthsDictionary[props.monthNumber as keyof typeof monthsDictionary] }}</div>
      <div
        :class="{
          'text-red-500': props.profit != null && props.profit < 0,
          'text-green-500': props.profit != null && props.profit >= 0,
        }"
      >
        {{ disabled ? "" : props.profit == null ? "-" : formatPLN(props.profit) }}
      </div>
    </div>
  </Button>
</template>
