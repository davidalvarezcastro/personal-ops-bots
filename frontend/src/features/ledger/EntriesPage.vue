<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";
import { computed } from "vue";
import { RouterLink } from "vue-router";

import { fetchEntries } from "./api";
import EntryRow from "./EntryRow.vue";

const entriesQuery = useQuery({
  queryKey: ["entries", "all"],
  queryFn: () => fetchEntries(null, 100),
});
const items = computed(() => entriesQuery.data.value?.items ?? []);
</script>

<template>
  <div class="mx-auto max-w-md space-y-4 p-4">
    <RouterLink class="text-sm underline" to="/">Home</RouterLink>
    <h1 class="text-xl font-semibold">All entries</h1>
    <ul class="space-y-2">
      <EntryRow v-for="entry in items" :key="entry.id" :entry="entry" />
    </ul>
  </div>
</template>
