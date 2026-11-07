<script setup lang="ts">
import { ref, watch } from "vue";

import type { LedgerEntry } from "./types";

const props = defineProps<{
  entry: LedgerEntry | null;
  categories: string[];
}>();
const emit = defineEmits<{
  close: [];
  save: [category: string];
}>();

const category = ref("Uncategorized");

watch(
  () => props.entry,
  (entry) => {
    if (entry) {
      category.value = entry.category;
    }
  },
  { immediate: true },
);
</script>

<template>
  <div v-if="entry" class="fixed inset-0 z-10 flex items-end bg-black/40" data-testid="edit-sheet">
    <form class="w-full rounded-t-3xl bg-white p-4" @submit.prevent="emit('save', category)">
      <h2 class="text-lg font-semibold">Edit {{ entry.payee }}</h2>
      <label class="mt-3 block text-sm">Category
        <select v-model="category" class="mt-1 w-full rounded border px-2 py-1" data-testid="edit-category">
          <option v-for="name in categories" :key="name" :value="name">{{ name }}</option>
        </select>
      </label>
      <div class="mt-4 flex gap-2">
        <button type="button" class="flex-1 rounded border py-2" @click="emit('close')">Cancel</button>
        <button type="submit" class="flex-1 rounded bg-stone-900 py-2 text-white" data-testid="edit-save">Save</button>
      </div>
    </form>
  </div>
</template>
