from income_expense_bot.application.unity_of_work import AbstractUnitOfWork


class BaseHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow
