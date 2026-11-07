export type EntryType = "expense" | "income";

export interface CategoryTotal {
  category: string;
  amount_cents: number;
}

export interface Balance {
  start: string;
  end: string;
  income_cents: number;
  expense_cents: number;
  net_cents: number;
  expense_by_category: CategoryTotal[];
  income_by_category: CategoryTotal[];
}

export interface LedgerEntry {
  id: string;
  type: EntryType;
  amount_cents: number;
  payee: string;
  category: string;
  payment_method: string;
  occurred_at: string;
}

export interface EntryPage {
  items: LedgerEntry[];
  next_cursor: string | null;
}

export function formatCents(cents: number): string {
  const sign = cents < 0 ? "-" : "";
  const abs = Math.abs(cents);
  const euros = Math.floor(abs / 100);
  const rest = String(abs % 100).padStart(2, "0");
  return `${sign}${euros},${rest} €`;
}

export function monthLabel(start: string): string {
  if (!start) {
    return "";
  }
  const [year, month] = start.split("-");
  const date = new Date(Date.UTC(Number(year), Number(month) - 1, 1));
  return date.toLocaleString("en-GB", { month: "long", year: "numeric", timeZone: "UTC" });
}
