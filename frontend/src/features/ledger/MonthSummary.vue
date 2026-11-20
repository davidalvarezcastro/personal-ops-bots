<script setup lang="ts">
import { formatCents, monthLabel, type Balance } from "./types";

defineProps<{ balance: Balance }>();
</script>

<template>
  <section class="space-y-3">
    <p class="text-sm text-stone-500">{{ monthLabel(balance.start) }}</p>
    <article
      v-for="group in balance.currencies"
      :key="group.currency"
      class="rounded-2xl bg-white p-4 shadow-sm"
      :data-testid="'currency-' + group.currency"
    >
      <p class="text-sm text-stone-500">{{ group.currency }}</p>
      <p class="mt-1 text-3xl font-semibold" data-testid="net">{{ formatCents(group.net_cents, group.currency) }}</p>
      <dl class="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div>
          <dt class="text-stone-500">Income</dt>
          <dd data-testid="income">{{ formatCents(group.income_cents, group.currency) }}</dd>
        </div>
        <div>
          <dt class="text-stone-500">Expense</dt>
          <dd data-testid="expense">{{ formatCents(group.expense_cents, group.currency) }}</dd>
        </div>
      </dl>
      <ul class="mt-3 space-y-1 text-sm" data-testid="categories">
        <li v-for="row in group.expense_by_category" :key="'e-' + row.category">
          {{ row.category }} {{ formatCents(row.amount_cents, group.currency) }}
        </li>
        <li v-for="row in group.income_by_category" :key="'i-' + row.category">
          {{ row.category }} {{ formatCents(row.amount_cents, group.currency) }}
        </li>
      </ul>
    </article>
  </section>
</template>
