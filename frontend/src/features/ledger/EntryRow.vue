<script setup lang="ts">
import { formatCents, type LedgerEntry } from "./types";

defineProps<{ entry: LedgerEntry }>();
const emit = defineEmits<{ edit: []; remove: [] }>();
</script>

<template>
  <li class="flex items-center justify-between gap-2 rounded-xl bg-white px-3 py-2 shadow-sm">
    <div>
      <p class="font-medium">{{ entry.payee }}</p>
      <p class="text-xs text-stone-500">{{ entry.category }} · {{ entry.type }}</p>
    </div>
    <div class="flex items-center gap-2">
      <span :class="entry.type === 'income' ? 'text-emerald-700' : 'text-rose-700'">
        {{ entry.type === "income" ? "+" : "-" }}{{ formatCents(entry.amount_cents) }}
      </span>
      <button type="button" class="text-sm underline" data-testid="edit" @click="emit('edit')">Edit</button>
      <button type="button" class="text-sm underline" data-testid="delete" @click="emit('remove')">Delete</button>
    </div>
  </li>
</template>
