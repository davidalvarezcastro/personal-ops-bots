from income_expense_bot.application.query.balance import BalanceResult, CurrencyBalance
from income_expense_bot.domain.model.currency import spec_for


def format_cents(cents: int, currency: str = "EUR") -> str:
    sign = "-" if cents < 0 else ""
    value = abs(cents)
    spec = spec_for(currency)
    if spec.exponent == 0:
        return f"{sign}{value} {currency}"
    return f"{sign}{value // 100},{value % 100:02d} {currency}"


def format_record_confirmation(
    *,
    kind: str,
    amount_cents: int,
    payee: str,
    category: str,
    currency: str = "EUR",
) -> str:
    return f"{kind} recorded: {format_cents(amount_cents, currency)} at {payee} ({category})"


def format_balance(result: BalanceResult) -> str:
    period = result.period
    if period.start == period.end:
        header = period.start.isoformat()
    else:
        header = f"{period.start.isoformat()} .. {period.end.isoformat()}"
    blocks = [header]
    for group in result.currencies:
        blocks.append(_format_currency_block(group))
    return "\n".join(blocks)


def _format_currency_block(group: CurrencyBalance) -> str:
    lines = [
        "",
        group.currency,
        f"Net: {format_cents(group.net_cents, group.currency)}",
        "",
        f"Income     {format_cents(group.income_cents, group.currency)}",
        f"Expense    {format_cents(group.expense_cents, group.currency)}",
    ]
    if group.expense_by_category:
        lines.extend(["", "Expense by category"])
        for item in group.expense_by_category:
            lines.append(f"  {item.category}  {format_cents(item.amount_cents, group.currency)}")
    if group.income_by_category:
        lines.extend(["", "Income by category"])
        for item in group.income_by_category:
            lines.append(f"  {item.category}  {format_cents(item.amount_cents, group.currency)}")
    return "\n".join(lines)
