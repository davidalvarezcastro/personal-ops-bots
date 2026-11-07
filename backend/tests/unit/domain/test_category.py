from income_expense_bot.domain.model.category import UNCATEGORIZED, split_category_and_payee
from income_expense_bot.domain.model.entry_type import EntryType


def test_multi_word_expense_category() -> None:
    category, payee = split_category_and_payee(EntryType.EXPENSE, "Food & Drinks Cafe Central")
    assert category == "Food & Drinks"
    assert payee == "Cafe Central"


def test_unknown_token_is_merchant() -> None:
    category, payee = split_category_and_payee(EntryType.EXPENSE, "Mercadona")
    assert category == UNCATEGORIZED
    assert payee == "Mercadona"


def test_income_category_not_valid_on_expense() -> None:
    category, payee = split_category_and_payee(EntryType.EXPENSE, "Salary Store")
    assert category == UNCATEGORIZED
    assert payee == "Salary Store"
