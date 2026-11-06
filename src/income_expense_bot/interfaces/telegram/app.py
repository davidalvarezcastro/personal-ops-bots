from __future__ import annotations

from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncEngine
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.application.handler.record_income import RecordIncomeHandler
from income_expense_bot.application.query.balance import LedgerBalanceQueryService
from income_expense_bot.config import Config
from income_expense_bot.infrastructure.database import (
    create_engine_from_config,
    create_schema,
    create_session_factory,
)
from income_expense_bot.infrastructure.read_model.balance_read_model import SqlBalanceReadModel
from income_expense_bot.infrastructure.unity_of_work import SqlAlchemyUnitOfWork
from income_expense_bot.interfaces.telegram.dispatch import TelegramDispatcher


def madrid_today() -> date:
    return datetime.now(ZoneInfo("Europe/Madrid")).date()


def build_dispatcher(config: Config) -> tuple[TelegramDispatcher, AsyncEngine]:
    engine = create_engine_from_config(config)
    session_factory = create_session_factory(engine)
    uow = SqlAlchemyUnitOfWork(session_factory)
    dispatcher = TelegramDispatcher(
        allowed_user_ids=config.telegram_allowed_user_ids,
        expense_handler=RecordExpenseHandler(uow),
        income_handler=RecordIncomeHandler(uow),
        balance_query=LedgerBalanceQueryService(
            read_model=SqlBalanceReadModel(session_factory),
            today_provider=madrid_today,
        ),
    )
    return dispatcher, engine


def build_ptb_application(
    config: Config,
    dispatcher: TelegramDispatcher,
    *,
    engine: AsyncEngine | None = None,
) -> Application[Any, Any, Any, Any, Any, Any]:
    builder = Application.builder().token(config.telegram_bot_token)
    if engine is not None:

        async def post_init(_application: Application[Any, Any, Any, Any, Any, Any]) -> None:
            await create_schema(engine)

        async def post_shutdown(_application: Application[Any, Any, Any, Any, Any, Any]) -> None:
            await engine.dispose()

        builder = builder.post_init(post_init).post_shutdown(post_shutdown)

    application = builder.build()

    async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async def reply(text: str) -> None:
            if update.message:
                await update.message.reply_text(text)

        user_id = update.effective_user.id if update.effective_user else None
        text = update.message.text if update.message and update.message.text else ""
        await dispatcher.handle_expense(user_id, text, reply)

    async def income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async def reply(text: str) -> None:
            if update.message:
                await update.message.reply_text(text)

        user_id = update.effective_user.id if update.effective_user else None
        text = update.message.text if update.message and update.message.text else ""
        await dispatcher.handle_income(user_id, text, reply)

    async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async def reply(text: str) -> None:
            if update.message:
                await update.message.reply_text(text)

        user_id = update.effective_user.id if update.effective_user else None
        text = update.message.text if update.message and update.message.text else ""
        await dispatcher.handle_balance(user_id, text, reply)

    application.add_handler(CommandHandler("expense", expense))
    application.add_handler(CommandHandler("income", income))
    application.add_handler(CommandHandler("balance", balance))
    return application


def run(config: Config | None = None) -> None:
    config = config or Config.from_env()
    dispatcher, engine = build_dispatcher(config)
    application = build_ptb_application(config, dispatcher, engine=engine)
    application.run_polling()
