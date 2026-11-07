<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";

import { createEntry, deleteEntry, fetchBalance, fetchCategories, fetchEntries, patchEntry } from "./api";
import CaptureSheet from "./CaptureSheet.vue";
import EditSheet from "./EditSheet.vue";
import EntryRow from "./EntryRow.vue";
import MonthSummary from "./MonthSummary.vue";
import type { EntryType, LedgerEntry } from "./types";

const queryClient = useQueryClient();
const captureType = ref<EntryType | null>(null);
const editing = ref<LedgerEntry | null>(null);
const pendingDelete = ref<LedgerEntry | null>(null);

const balanceQuery = useQuery({ queryKey: ["balance"], queryFn: fetchBalance });
const entriesQuery = useQuery({ queryKey: ["entries", "home"], queryFn: () => fetchEntries(null, 8) });
const captureCategories = useQuery({
  queryKey: ["categories", captureType],
  queryFn: () => fetchCategories(captureType.value ?? "expense"),
  enabled: computed(() => captureType.value !== null),
});
const editCategories = useQuery({
  queryKey: ["categories", computed(() => editing.value?.type)],
  queryFn: () => fetchCategories(editing.value?.type ?? "expense"),
  enabled: computed(() => editing.value !== null),
});

const extraEntries = ref<LedgerEntry[]>([]);
const balance = computed(() => balanceQuery.data.value);
const isBalancePending = computed(() => balanceQuery.isPending.value);
const nextCursor = computed(() => entriesQuery.data.value?.next_cursor ?? null);
const captureCategoryList = computed(() => captureCategories.data.value?.categories ?? ["Uncategorized"]);
const editCategoryList = computed(() => editCategories.data.value?.categories ?? ["Uncategorized"]);

async function loadMore() {
  const cursor = nextCursor.value;
  if (!cursor) {
    return;
  }
  const page = await fetchEntries(cursor, 8);
  extraEntries.value = [...extraEntries.value, ...page.items];
  await queryClient.setQueryData(["entries", "home"], {
    items: entriesQuery.data.value?.items ?? [],
    next_cursor: page.next_cursor,
  });
}

const rows = computed(() => [...(entriesQuery.data.value?.items ?? []), ...extraEntries.value]);

function invalidate() {
  extraEntries.value = [];
  void queryClient.invalidateQueries({ queryKey: ["balance"] });
  void queryClient.invalidateQueries({ queryKey: ["entries"] });
}

const saveMutation = useMutation({
  mutationFn: (payload: { amount: string; payee: string; category: string }) =>
    createEntry({
      type: captureType.value ?? "expense",
      amount: payload.amount,
      payee: payload.payee,
      category: payload.category,
    }),
  onSuccess: () => {
    captureType.value = null;
    invalidate();
  },
});

const editMutation = useMutation({
  mutationFn: (category: string) => patchEntry(editing.value!.id, category),
  onSuccess: () => {
    editing.value = null;
    invalidate();
  },
});

const deleteMutation = useMutation({
  mutationFn: (id: string) => deleteEntry(id),
  onSuccess: () => {
    pendingDelete.value = null;
    invalidate();
  },
});
</script>

<template>
  <div class="mx-auto max-w-md space-y-4 p-4">
    <MonthSummary
      v-if="balance"
      :balance="balance"
    />
    <p v-else-if="isBalancePending">Loading…</p>
    <section>
      <div class="mb-2 flex items-center justify-between">
        <h2 class="font-semibold">Recent</h2>
        <RouterLink class="text-sm underline" to="/entries">See more</RouterLink>
      </div>
      <ul class="space-y-2" data-testid="recent-list">
        <EntryRow
          v-for="entry in rows"
          :key="entry.id"
          :entry="entry"
          @edit="editing = entry"
          @remove="pendingDelete = entry"
        />
      </ul>
      <button
        v-if="nextCursor"
        type="button"
        class="mt-3 w-full rounded border py-2"
        data-testid="see-more"
        @click="loadMore"
      >
        See more
      </button>
    </section>
    <div class="fixed bottom-4 left-1/2 flex -translate-x-1/2 gap-6">
      <button
        type="button"
        class="h-14 w-14 rounded-full bg-rose-600 text-2xl text-white"
        data-testid="add-expense"
        @click="captureType = 'expense'"
      >
        −
      </button>
      <button
        type="button"
        class="h-14 w-14 rounded-full bg-emerald-600 text-2xl text-white"
        data-testid="add-income"
        @click="captureType = 'income'"
      >
        +
      </button>
    </div>
    <CaptureSheet
      :open="captureType !== null"
      :entry-type="captureType ?? 'expense'"
      :categories="captureCategoryList"
      @close="captureType = null"
      @save="saveMutation.mutate"
    />
    <EditSheet
      :entry="editing"
      :categories="editCategoryList"
      @close="editing = null"
      @save="editMutation.mutate"
    />
    <div v-if="pendingDelete" class="fixed inset-0 z-20 flex items-center justify-center bg-black/40" data-testid="confirm-delete">
      <div class="rounded-xl bg-white p-4">
        <p>Delete {{ pendingDelete.payee }}?</p>
        <div class="mt-3 flex gap-2">
          <button type="button" class="rounded border px-3 py-1" @click="pendingDelete = null">Cancel</button>
          <button
            type="button"
            class="rounded bg-rose-600 px-3 py-1 text-white"
            data-testid="confirm-delete-yes"
            @click="deleteMutation.mutate(pendingDelete.id)"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
