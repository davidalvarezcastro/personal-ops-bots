import { createRouter, createWebHistory } from "vue-router";

import EntriesPage from "./features/ledger/EntriesPage.vue";
import HomePage from "./features/ledger/HomePage.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomePage },
    { path: "/entries", name: "entries", component: EntriesPage },
  ],
});
