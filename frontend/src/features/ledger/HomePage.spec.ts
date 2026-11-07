import { VueQueryPlugin, QueryClient } from "@tanstack/vue-query";
import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createMemoryHistory, createRouter } from "vue-router";

import * as api from "./api";
import CaptureSheet from "./CaptureSheet.vue";
import HomePage from "./HomePage.vue";
import type { Balance, LedgerEntry } from "./types";

vi.mock("./api", () => ({
  fetchBalance: vi.fn(),
  fetchEntries: vi.fn(),
  fetchCategories: vi.fn(),
  createEntry: vi.fn(),
  patchEntry: vi.fn(),
  deleteEntry: vi.fn(),
}));

function entry(partial: Partial<LedgerEntry> & { id: string; payee: string }): LedgerEntry {
  return {
    type: "expense",
    amount_cents: 100,
    category: "Uncategorized",
    payment_method: "card",
    occurred_at: "2026-11-07T10:00:00+00:00",
    ...partial,
  };
}

const emptyBalance: Balance = {
  start: "2026-11-01",
  end: "2026-11-30",
  income_cents: 0,
  expense_cents: 0,
  net_cents: 0,
  expense_by_category: [],
  income_by_category: [],
};

async function mountHome() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: HomePage },
      { path: "/entries", component: { template: "<div />" } },
    ],
  });
  await router.push("/");
  await router.isReady();
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return mount(HomePage, {
    global: {
      plugins: [router, [VueQueryPlugin, { queryClient }]],
    },
  });
}

describe("HomePage", () => {
  beforeEach(() => {
    vi.mocked(api.fetchBalance).mockResolvedValue(emptyBalance);
    vi.mocked(api.fetchEntries).mockResolvedValue({ items: [], next_cursor: null });
    vi.mocked(api.fetchCategories).mockResolvedValue({ type: "expense", categories: ["Uncategorized", "Groceries", "Transport"] });
    vi.mocked(api.createEntry).mockResolvedValue(entry({ id: "new", payee: "Mercadona", category: "Groceries", amount_cents: 1250 }));
    vi.mocked(api.patchEntry).mockResolvedValue(entry({ id: "1", payee: "Shop", category: "Transport" }));
    vi.mocked(api.deleteEntry).mockResolvedValue(undefined);
  });

  it("shows November zeros when empty", async () => {
    const wrapper = await mountHome();
    await flushPromises();
    expect(wrapper.text()).toContain("November 2026");
    expect(wrapper.get('[data-testid="net"]').text()).toContain("0,00");
    expect(wrapper.get('[data-testid="income"]').text()).toContain("0,00");
    expect(wrapper.get('[data-testid="expense"]').text()).toContain("0,00");
    expect(wrapper.get('[data-testid="recent-list"]').findAll("li")).toHaveLength(0);
  });

  it("lists eight recent rows", async () => {
    vi.mocked(api.fetchEntries).mockResolvedValue({
      items: Array.from({ length: 8 }, (_, index) => entry({ id: String(index), payee: `Shop ${index}` })),
      next_cursor: "cursor-1",
    });
    const wrapper = await mountHome();
    await flushPromises();
    expect(wrapper.get('[data-testid="recent-list"]').findAll("li")).toHaveLength(8);
  });

  it("loads older rows via next_cursor without duplicating the first eight", async () => {
    const first = Array.from({ length: 8 }, (_, index) => entry({ id: `a${index}`, payee: `A ${index}` }));
    const second = Array.from({ length: 4 }, (_, index) => entry({ id: `b${index}`, payee: `B ${index}` }));
    vi.mocked(api.fetchEntries)
      .mockResolvedValueOnce({ items: first, next_cursor: "c1" })
      .mockResolvedValueOnce({ items: second, next_cursor: null });
    const wrapper = await mountHome();
    await flushPromises();
    await wrapper.get('[data-testid="see-more"]').trigger("click");
    await flushPromises();
    const labels = wrapper.get('[data-testid="recent-list"]').findAll("li").map((node) => node.text());
    expect(labels.filter((text) => text.includes("A 0"))).toHaveLength(1);
    expect(labels.some((text) => text.includes("B 0"))).toBe(true);
    expect(wrapper.get('[data-testid="recent-list"]').findAll("li")).toHaveLength(12);
  });

  it("saves a grocery expense from the capture sheet", async () => {
    const wrapper = await mountHome();
    await flushPromises();
    await wrapper.get('[data-testid="add-expense"]').trigger("click");
    await flushPromises();
    const sheet = wrapper.getComponent(CaptureSheet);
    await sheet.get('[data-testid="amount"]').setValue("12,50");
    await sheet.get('[data-testid="payee"]').setValue("Mercadona");
    await sheet.get('[data-testid="category"]').setValue("Groceries");
    await sheet.get("form").trigger("submit");
    await flushPromises();
    expect(api.createEntry).toHaveBeenCalledWith({
      type: "expense",
      amount: "12,50",
      payee: "Mercadona",
      category: "Groceries",
    });
  });

  it("income capture excludes Groceries", async () => {
    vi.mocked(api.fetchCategories).mockImplementation(async (type) => {
      if (type === "income") {
        return { type: "income", categories: ["Uncategorized", "Salary"] };
      }
      return { type: "expense", categories: ["Uncategorized", "Groceries"] };
    });
    const wrapper = await mountHome();
    await flushPromises();
    await wrapper.get('[data-testid="add-income"]').trigger("click");
    await flushPromises();
    const options = wrapper.get('[data-testid="category"]').findAll("option").map((node) => node.text());
    expect(options).toContain("Salary");
    expect(options).not.toContain("Groceries");
  });

  it("recategorizes Uncategorized to Transport", async () => {
    vi.mocked(api.fetchEntries).mockResolvedValue({
      items: [entry({ id: "1", payee: "Shop", category: "Uncategorized" })],
      next_cursor: null,
    });
    const wrapper = await mountHome();
    await flushPromises();
    await wrapper.get('[data-testid="edit"]').trigger("click");
    await flushPromises();
    await wrapper.get('[data-testid="edit-category"]').setValue("Transport");
    await wrapper.get('[data-testid="edit-sheet"]').get("form").trigger("submit");
    await flushPromises();
    expect(api.patchEntry).toHaveBeenCalledWith("1", "Transport");
  });

  it("removes a row after confirm delete", async () => {
    vi.mocked(api.fetchEntries).mockResolvedValue({
      items: [entry({ id: "1", payee: "Shop" })],
      next_cursor: null,
    });
    const wrapper = await mountHome();
    await flushPromises();
    await wrapper.get('[data-testid="delete"]').trigger("click");
    await wrapper.get('[data-testid="confirm-delete-yes"]').trigger("click");
    await flushPromises();
    expect(api.deleteEntry).toHaveBeenCalledWith("1");
  });
});
