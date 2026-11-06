from income_expense_bot.domain.exception.ledger import UnauthorizedError


def require_authorized(user_id: int | None, allowed: frozenset[int]) -> int:
    if user_id is None or user_id not in allowed:
        raise UnauthorizedError("operator is not allowlisted")
    return user_id
