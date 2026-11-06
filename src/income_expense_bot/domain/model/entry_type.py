from enum import StrEnum


class EntryType(StrEnum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"


class PaymentMethod(StrEnum):
    CARD = "card"
    CASH = "cash"
    BANK_TRANSFER = "bank transfer"
