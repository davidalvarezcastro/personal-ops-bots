from __future__ import annotations

from income_expense_bot.domain.model.entry_type import EntryType

UNCATEGORIZED = "Uncategorized"

EXPENSE_CATEGORIES: tuple[str, ...] = (
    UNCATEGORIZED,
    "Food & Drinks",
    "Groceries",
    "Transport",
    "Shopping",
    "Entertainment",
    "Health",
    "Personal Care",
    "Bills & Utilities",
    "Subscriptions",
    "Travel",
    "Education",
)

INCOME_CATEGORIES: tuple[str, ...] = (
    UNCATEGORIZED,
    "Salary",
    "Bonus",
    "Interest",
    "Gifts",
    "Refunds",
)


def catalog_for(entry_type: EntryType) -> tuple[str, ...]:
    if entry_type is EntryType.EXPENSE:
        return EXPENSE_CATEGORIES
    if entry_type is EntryType.INCOME:
        return INCOME_CATEGORIES
    return (UNCATEGORIZED,)


def split_category_and_payee(entry_type: EntryType, remainder: str) -> tuple[str, str]:
    text = remainder.strip()
    if not text:
        return UNCATEGORIZED, ""
    tokens = text.split()
    catalog = catalog_for(entry_type)
    lookup = {name.casefold(): name for name in catalog}
    longest = 0
    matched = UNCATEGORIZED
    for size in range(1, len(tokens) + 1):
        prefix = " ".join(tokens[:size]).casefold()
        if prefix in lookup:
            longest = size
            matched = lookup[prefix]
    if longest:
        payee = " ".join(tokens[longest:]).strip()
        return matched, payee
    return UNCATEGORIZED, text
