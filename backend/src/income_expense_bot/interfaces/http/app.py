from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from income_expense_bot.application.commands import (
    ChangeEntryCategoryCommand,
    DeleteLedgerEntryCommand,
    RecordExpenseCommand,
    RecordIncomeCommand,
)
from income_expense_bot.application.handler.change_entry_category import ChangeEntryCategoryHandler
from income_expense_bot.application.handler.delete_ledger_entry import DeleteLedgerEntryHandler
from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.application.handler.record_income import RecordIncomeHandler
from income_expense_bot.application.query.balance import LedgerBalanceQueryService
from income_expense_bot.application.query.entries import LedgerEntryListQueryService
from income_expense_bot.application.query.period import parse_iso_date
from income_expense_bot.config import Config
from income_expense_bot.domain.exception.ledger import (
    EntryNotFoundError,
    InvalidAmountError,
    InvalidCategoryError,
    InvalidCursorError,
    InvalidDateFormatError,
    InvalidDateRangeError,
    MissingPayeeError,
)
from income_expense_bot.domain.model.category import UNCATEGORIZED, catalog_for
from income_expense_bot.domain.model.entry_type import EntryType
from income_expense_bot.domain.model.money import Money
from income_expense_bot.infrastructure.database import (
    create_engine_from_config,
    create_schema,
    create_session_factory,
)
from income_expense_bot.infrastructure.read_model.balance_read_model import SqlBalanceReadModel
from income_expense_bot.infrastructure.unity_of_work import SqlAlchemyUnitOfWork
from income_expense_bot.interfaces.http.schemas import (
    BalanceCategoryOut,
    BalanceOut,
    EntryCreate,
    EntryOut,
    EntryPageOut,
    EntryPatch,
    entry_to_out,
)


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [part.strip() for part in raw.split(",") if part.strip()]


def _madrid_today() -> datetime:
    return datetime.now(ZoneInfo("Europe/Madrid"))


def create_app(config: Config | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        settings = config or Config.from_env()
        engine = create_engine_from_config(settings)
        await create_schema(engine)
        app.state.config = settings
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)
        yield
        await engine.dispose()

    application = FastAPI(title="income-expense ledger", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(EntryNotFoundError)
    async def _not_found(_request: Request, exc: EntryNotFoundError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=404)

    @application.exception_handler(InvalidCategoryError)
    async def _bad_category(_request: Request, exc: InvalidCategoryError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @application.exception_handler(MissingPayeeError)
    async def _missing_payee(_request: Request, exc: MissingPayeeError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @application.exception_handler(InvalidDateRangeError)
    async def _bad_range(_request: Request, exc: InvalidDateRangeError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @application.exception_handler(InvalidDateFormatError)
    async def _bad_date(_request: Request, exc: InvalidDateFormatError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @application.exception_handler(InvalidCursorError)
    async def _bad_cursor(_request: Request, exc: InvalidCursorError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @application.exception_handler(InvalidAmountError)
    async def _bad_amount(_request: Request, exc: InvalidAmountError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=422)

    def _uow(request: Request) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(request.app.state.session_factory)

    def _balance_service(request: Request) -> LedgerBalanceQueryService:
        return LedgerBalanceQueryService(
            SqlBalanceReadModel(request.app.state.session_factory),
            today_provider=lambda: _madrid_today().date(),
        )

    @application.get("/api/v1/balance", response_model=BalanceOut)
    async def get_balance(
        request: Request,
        start: str | None = None,
        end: str | None = None,
    ) -> BalanceOut:
        start_date = parse_iso_date(start) if start else None
        end_date = parse_iso_date(end) if end else None
        result = await _balance_service(request).get(start_date, end_date)
        return BalanceOut(
            start=result.period.start.isoformat(),
            end=result.period.end.isoformat(),
            income_cents=result.income_cents,
            expense_cents=result.expense_cents,
            net_cents=result.net_cents,
            expense_by_category=[
                BalanceCategoryOut(category=row.category, amount_cents=row.amount_cents)
                for row in result.expense_by_category
            ],
            income_by_category=[
                BalanceCategoryOut(category=row.category, amount_cents=row.amount_cents)
                for row in result.income_by_category
            ],
        )

    @application.get("/api/v1/entries", response_model=EntryPageOut)
    async def list_entries(
        request: Request,
        limit: int | None = Query(default=None),
        cursor: str | None = None,
    ) -> EntryPageOut:
        uow = _uow(request)
        async with uow as unit:
            page = await LedgerEntryListQueryService(unit.entries).get(limit=limit, cursor=cursor)
        return EntryPageOut(
            items=[entry_to_out(item) for item in page.items],
            next_cursor=page.next_cursor,
        )

    @application.post("/api/v1/entries", response_model=EntryOut, status_code=201)
    async def create_entry(request: Request, body: EntryCreate) -> EntryOut:
        money = Money.parse(body.amount)
        entry_type = EntryType(body.type)
        raw_category = body.category.strip() if body.category else UNCATEGORIZED
        lookup = {name.casefold(): name for name in catalog_for(entry_type)}
        category = lookup.get(raw_category.casefold())
        if category is None:
            raise InvalidCategoryError(f"category is not allowed for {entry_type}: {raw_category}")
        uow = _uow(request)
        if body.type == "expense":
            await RecordExpenseHandler(uow).handle(
                RecordExpenseCommand(amount_cents=money.cents, payee=body.payee, category=category)
            )
        else:
            await RecordIncomeHandler(uow).handle(
                RecordIncomeCommand(amount_cents=money.cents, payee=body.payee, category=category)
            )
        async with uow as unit:
            page = await LedgerEntryListQueryService(unit.entries).get(limit=1)
        return entry_to_out(page.items[0])

    @application.patch("/api/v1/entries/{entry_id}", response_model=EntryOut)
    async def patch_entry(request: Request, entry_id: str, body: EntryPatch) -> EntryOut:
        uow = _uow(request)
        await ChangeEntryCategoryHandler(uow).handle(
            ChangeEntryCategoryCommand(entry_id=entry_id, category=body.category)
        )
        async with uow as unit:
            entry = await unit.entries.get(entry_id)
        if entry is None:
            raise EntryNotFoundError(f"entry not found: {entry_id}")
        return entry_to_out(entry)

    @application.delete("/api/v1/entries/{entry_id}", status_code=204)
    async def delete_entry(request: Request, entry_id: str) -> None:
        await DeleteLedgerEntryHandler(_uow(request)).handle(DeleteLedgerEntryCommand(entry_id=entry_id))

    @application.get("/api/v1/categories")
    async def list_categories(type: str = Query(..., alias="type")) -> dict[str, Any]:
        try:
            entry_type = EntryType(type)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="type must be expense or income") from exc
        return {"type": entry_type.value, "categories": list(catalog_for(entry_type))}

    return application


app = create_app()
