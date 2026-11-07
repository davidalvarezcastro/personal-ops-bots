from income_expense_bot.application.query.balance import BalanceResult


def format_cents(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    value = abs(cents)
    return f"{sign}{value // 100},{value % 100:02d}"


def format_record_confirmation(*, kind: str, amount_cents: int, payee: str, category: str) -> str:
    return (
        f"{kind} recorded: {format_cents(amount_cents)} EUR "
        f"at {payee} ({category})"
    )


def format_balance(result: BalanceResult) -> str:
    period = result.period
    if period.start == period.end:
        header = period.start.isoformat()
    else:
        header = f"{period.start.isoformat()} .. {period.end.isoformat()}"
    lines = [
        header,
        f"Net: {format_cents(result.net_cents)} EUR",
        "",
        f"Income     {format_cents(result.income_cents)}",
        f"Expense    {format_cents(result.expense_cents)}",
    ]
    if result.expense_by_category:
        lines.extend(["", "Expense by category"])
        for item in result.expense_by_category:
            lines.append(f"  {item.category}  {format_cents(item.amount_cents)}")
    if result.income_by_category:
        lines.extend(["", "Income by category"])
        for item in result.income_by_category:
            lines.append(f"  {item.category}  {format_cents(item.amount_cents)}")
    return "\n".join(lines)
