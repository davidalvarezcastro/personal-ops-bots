class LedgerError(Exception):
    """Base domain error."""


class InvalidAmountError(LedgerError):
    """Amount text is not a valid euro amount with at most two decimals."""


class MissingPayeeError(LedgerError):
    """Merchant or income source is required."""


class InvalidDateFormatError(LedgerError):
    """A balance date is not YYYY-MM-DD."""


class InvalidDateRangeError(LedgerError):
    """Balance end date is before start date."""


class UnauthorizedError(LedgerError):
    """Operator is not allowlisted."""


class InvalidCategoryError(LedgerError):
    """Category is not in the catalog for this entry type."""


class EntryNotFoundError(LedgerError):
    """No ledger entry exists for the given id."""


class InvalidCursorError(LedgerError):
    """List cursor is malformed."""
