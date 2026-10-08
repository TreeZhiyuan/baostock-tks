"""DuckDB persistence for Baostock historical A-share K-line data."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import duckdb

from stock_basic_info.database import DEFAULT_DATABASE, PROJECT_ROOT


DDL_FILE = PROJECT_ROOT / "duckdb" / "ddl" / "history_k_data.sql"


def save_history_k_data(
    records: Iterable[dict[str, Any]], database_path: Path = DEFAULT_DATABASE
) -> int:
    """Create the K-line table and insert/update records idempotently."""
    rows = [
        (
            record["trade_date"],
            record.get("trade_time", ""),
            record["code"],
            record["frequency"].lower(),
            record.get("open"),
            record.get("high"),
            record.get("low"),
            record.get("close"),
            record.get("preclose"),
            record.get("volume"),
            record.get("amount"),
            int(record["adjustflag"]),
            record.get("turn"),
            record.get("tradestatus"),
            record.get("pct_chg"),
            record.get("pe_ttm"),
            record.get("ps_ttm"),
            record.get("pcf_ncf_ttm"),
            record.get("pb_mrq"),
            record.get("is_st"),
        )
        for record in records
    ]
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(database_path)) as connection:
        connection.execute(DDL_FILE.read_text(encoding="utf-8"))
        if rows:
            connection.executemany(
                """
                INSERT INTO history_k_data (
                    trade_date, trade_time, code, frequency,
                    open, high, low, close, preclose, volume, amount,
                    adjustflag, turn, tradestatus, pct_chg,
                    pe_ttm, ps_ttm, pcf_ncf_ttm, pb_mrq, is_st
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (code, frequency, adjustflag, trade_date, trade_time)
                DO UPDATE SET
                    open = excluded.open,
                    high = excluded.high,
                    low = excluded.low,
                    close = excluded.close,
                    preclose = excluded.preclose,
                    volume = excluded.volume,
                    amount = excluded.amount,
                    turn = excluded.turn,
                    tradestatus = excluded.tradestatus,
                    pct_chg = excluded.pct_chg,
                    pe_ttm = excluded.pe_ttm,
                    ps_ttm = excluded.ps_ttm,
                    pcf_ncf_ttm = excluded.pcf_ncf_ttm,
                    pb_mrq = excluded.pb_mrq,
                    is_st = excluded.is_st
                """,
                rows,
            )
    return len(rows)
