import type { Balance, EntryPage, EntryType, LedgerEntry } from "./types";

const base = () => import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (response.status === 204) {
    return undefined as T;
  }
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || response.statusText);
  }
  return (await response.json()) as T;
}

export function fetchBalance(): Promise<Balance> {
  return request<Balance>("/api/v1/balance");
}

export function fetchEntries(cursor?: string | null, limit = 8): Promise<EntryPage> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (cursor) {
    params.set("cursor", cursor);
  }
  return request<EntryPage>(`/api/v1/entries?${params.toString()}`);
}

export function fetchCategories(type: EntryType): Promise<{ type: string; categories: string[] }> {
  return request(`/api/v1/categories?type=${type}`);
}

export function createEntry(body: {
  type: EntryType;
  amount: string;
  payee: string;
  category?: string;
}): Promise<LedgerEntry> {
  return request<LedgerEntry>("/api/v1/entries", { method: "POST", body: JSON.stringify(body) });
}

export function patchEntry(id: string, category: string): Promise<LedgerEntry> {
  return request<LedgerEntry>(`/api/v1/entries/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ category }),
  });
}

export function deleteEntry(id: string): Promise<void> {
  return request<void>(`/api/v1/entries/${id}`, { method: "DELETE" });
}
