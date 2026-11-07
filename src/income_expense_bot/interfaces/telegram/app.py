from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncEngine
from telegram import BotCommand, Update
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
from income_expense_bot.logging_config import configure_logging, get_logger

MENU_COMMANDS = [
    BotCommand("start", "Welcome; confirm the bot is ready"),
    BotCommand("help", "List commands and syntax"),
    BotCommand("expense", "Record an expense"),
    BotCommand("income", "Record income"),
    BotCommand("balance", "Show net and category totals"),
]


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


async def complete_startup(
    application: Application[Any, Any, Any, Any, Any, Any],
    *,
    engine: AsyncEngine | None = None,
) -> None:
    if engine is not None:
        await create_schema(engine)
    await application.bot.set_my_commands(MENU_COMMANDS)
    get_logger(__name__).info("bot.running", component="telegram")


def build_ptb_application(
    config: Config,
    dispatcher: TelegramDispatcher,
    *,
    engine: AsyncEngine | None = None,
) -> Application[Any, Any, Any, Any, Any, Any]:
    builder = Application.builder().token(config.telegram_bot_token)

    async def post_init(application: Application[Any, Any, Any, Any, Any, Any]) -> None:
        await complete_startup(application, engine=engine)

    builder = builder.post_init(post_init)
    if engine is not None:

        async def post_shutdown(_application: Application[Any, Any, Any, Any, Any, Any]) -> None:
            await engine.dispose()

        builder = builder.post_shutdown(post_shutdown)

    application = builder.build()

    def bind(
        handle: Callable[[int | None, str, Callable[[str], Awaitable[None]]], Awaitable[None]],
    ) -> Callable[[Update, ContextTypes.DEFAULT_TYPE], Coroutine[Any, Any, None]]:
        async def inner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            async def reply(text: str) -> None:
                if update.message:
                    await update.message.reply_text(text)

            user_id = update.effective_user.id if update.effective_user else None
            text = update.message.text if update.message and update.message.text else ""
            await handle(user_id, text, reply)

        return inner

    application.add_handler(CommandHandler("start", bind(dispatcher.handle_start)))
    application.add_handler(CommandHandler("help", bind(dispatcher.handle_help)))
    application.add_handler(CommandHandler("expense", bind(dispatcher.handle_expense)))
    application.add_handler(CommandHandler("income", bind(dispatcher.handle_income)))
    application.add_handler(CommandHandler("balance", bind(dispatcher.handle_balance)))
    return application


def run(config: Config | None = None) -> None:
    configure_logging()
    config = config or Config.from_env()
    dispatcher, engine = build_dispatcher(config)
    application = build_ptb_application(config, dispatcher, engine=engine)
    application.run_polling()
