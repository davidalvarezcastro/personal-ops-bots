<script setup lang="ts">
import { formatCents, monthLabel, type Balance } from "./types";

defineProps<{ balance: Balance }>();
</script>

<template>
  <section class="rounded-2xl bg-white p-4 shadow-sm">
    <p class="text-sm text-stone-500">{{ monthLabel(balance.start) }}</p>
    <p class="mt-1 text-3xl font-semibold" data-testid="net">{{ formatCents(balance.net_cents) }}</p>
    <dl class="mt-3 grid grid-cols-2 gap-2 text-sm">
      <div>
        <dt class="text-stone-500">Income</dt>
        <dd data-testid="income">{{ formatCents(balance.income_cents) }}</dd>
      </div>
      <div>
        <dt class="text-stone-500">Expense</dt>
        <dd data-testid="expense">{{ formatCents(balance.expense_cents) }}</dd>
      </div>
    </dl>
    <ul class="mt-3 space-y-1 text-sm" data-testid="categories">
      <li v-for="row in balance.expense_by_category" :key="'e-' + row.category">
        {{ row.category }} {{ formatCents(row.amount_cents) }}
      </li>
      <li v-for="row in balance.income_by_category" :key="'i-' + row.category">
        {{ row.category }} {{ formatCents(row.amount_cents) }}
      </li>
    </ul>
  </section>
</template>
