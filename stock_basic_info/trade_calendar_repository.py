"""DuckDB persistence for Baostock trading calendar data."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import duckdb

from stock_basic_info.database import DEFAULT_DATABASE, PROJECT_ROOT
DDL_FILE = PROJECT_ROOT / "duckdb" / "ddl" / "trade_calendar.sql"


def save_trade_calendar(
    records: Iterable[dict[str, Any]], database_path: Path = DEFAULT_DATABASE
) -> int:
    """Create the calendar table and insert/update trading-day flags."""
    rows = [
        (record["calendar_date"], record["is_trading_day"]) for record in records
    ]
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(database_path)) as connection:
        connection.execute(DDL_FILE.read_text(encoding="utf-8"))
        if rows:
            connection.executemany(
                """
                INSERT INTO trade_calendar (calendar_date, is_trading_day)
                VALUES (?, ?)
                ON CONFLICT (calendar_date) DO UPDATE SET
                    is_trading_day = excluded.is_trading_day
                """,
                rows,
            )
    return len(rows)
