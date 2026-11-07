<script setup lang="ts">
import { computed, ref, watch } from "vue";

import type { EntryType } from "./types";

const props = defineProps<{
  open: boolean;
  entryType: EntryType;
  categories: string[];
}>();
const emit = defineEmits<{
  close: [];
  save: [payload: { amount: string; payee: string; category: string }];
}>();

const amount = ref("");
const payee = ref("");
const category = ref("Uncategorized");
const title = computed(() => (props.entryType === "expense" ? "Expense" : "Income"));

watch(
  () => props.open,
  (open) => {
    if (open) {
      amount.value = "";
      payee.value = "";
      category.value = "Uncategorized";
    }
  },
);

function submit() {
  emit("save", { amount: amount.value, payee: payee.value, category: category.value });
}
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-10 flex items-end bg-black/40" data-testid="capture-sheet">
    <form class="w-full rounded-t-3xl bg-white p-4" @submit.prevent="submit">
      <h2 class="text-lg font-semibold">{{ title }}</h2>
      <label class="mt-3 block text-sm">Amount
        <input v-model="amount" class="mt-1 w-full rounded border px-2 py-1" data-testid="amount" required />
      </label>
      <label class="mt-3 block text-sm">{{ entryType === "expense" ? "Merchant" : "Source" }}
        <input v-model="payee" class="mt-1 w-full rounded border px-2 py-1" data-testid="payee" required />
      </label>
      <label class="mt-3 block text-sm">Category
        <select v-model="category" class="mt-1 w-full rounded border px-2 py-1" data-testid="category">
          <option v-for="name in categories" :key="name" :value="name">{{ name }}</option>
        </select>
      </label>
      <div class="mt-4 flex gap-2">
        <button type="button" class="flex-1 rounded border py-2" @click="emit('close')">Cancel</button>
        <button type="submit" class="flex-1 rounded bg-stone-900 py-2 text-white" data-testid="save">Save</button>
      </div>
    </form>
  </div>
</template>
