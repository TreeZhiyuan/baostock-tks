"""DuckDB persistence for daily security basic information."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import duckdb

from stock_basic_info.database import DEFAULT_DATABASE, PROJECT_ROOT
DDL_FILE = PROJECT_ROOT / "duckdb" / "ddl" / "stock_basic_info.sql"


def save_stock_basic_info(
    records: Iterable[dict[str, Any]], database_path: Path = DEFAULT_DATABASE
) -> int:
    """Create the documented table and insert/update a day's security snapshot."""
    rows = [
        (
            record["query_date"],
            record["code"],
            record.get("trade_status"),
            record.get("code_name"),
        )
        for record in records
    ]
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(database_path)) as connection:
        connection.execute(DDL_FILE.read_text(encoding="utf-8"))
        if rows:
            connection.executemany(
                """
                INSERT INTO stock_basic_info
                    (query_date, code, trade_status, code_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (query_date, code) DO UPDATE SET
                    trade_status = excluded.trade_status,
                    code_name = excluded.code_name
                """,
                rows,
            )
    return len(rows)
