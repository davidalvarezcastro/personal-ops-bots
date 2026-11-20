export type EntryType = "expense" | "income";

export const CURRENCIES = ["EUR", "USD", "GBP", "JPY", "CNY"] as const;
export type CurrencyCode = (typeof CURRENCIES)[number];

const EXPONENTS: Record<string, number> = {
  EUR: 2,
  USD: 2,
  GBP: 2,
  JPY: 0,
  CNY: 2,
};

export interface CategoryTotal {
  category: string;
  amount_cents: number;
}

export interface CurrencyBalance {
  currency: string;
  income_cents: number;
  expense_cents: number;
  net_cents: number;
  expense_by_category: CategoryTotal[];
  income_by_category: CategoryTotal[];
}

export interface Balance {
  start: string;
  end: string;
  currencies: CurrencyBalance[];
}

export interface LedgerEntry {
  id: string;
  type: EntryType;
  amount_cents: number;
  currency: string;
  payee: string;
  category: string;
  payment_method: string;
  occurred_at: string;
}

export interface EntryPage {
  items: LedgerEntry[];
  next_cursor: string | null;
}

export function formatCents(cents: number, currency = "EUR"): string {
  const sign = cents < 0 ? "-" : "";
  const abs = Math.abs(cents);
  const exponent = EXPONENTS[currency] ?? 2;
  if (exponent === 0) {
    return `${sign}${abs} ${currency}`;
  }
  const factor = 10 ** exponent;
  const whole = Math.floor(abs / factor);
  const rest = String(abs % factor).padStart(exponent, "0");
  return `${sign}${whole},${rest} ${currency}`;
}

export function monthLabel(start: string): string {
  if (!start) {
    return "";
  }
  const [year, month] = start.split("-");
  const date = new Date(Date.UTC(Number(year), Number(month) - 1, 1));
  return date.toLocaleString("en-GB", { month: "long", year: "numeric", timeZone: "UTC" });
}
