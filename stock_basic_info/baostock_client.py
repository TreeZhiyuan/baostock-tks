"""Baostock API client operations."""

from __future__ import annotations

from datetime import date
import time
from typing import Any

import baostock as bs


NETWORK_ERROR_CODES = {"10002007"}


def _login(login_retries: int, retry_delay: float) -> None:
    if login_retries < 1:
        raise ValueError("login_retries must be at least 1")

    login_result = None
    for attempt in range(1, login_retries + 1):
        login_result = bs.login()
        if login_result.error_code == "0":
            return
        if login_result.error_code in NETWORK_ERROR_CODES and attempt < login_retries:
            time.sleep(retry_delay)

    raise RuntimeError(
        f"Baostock login failed ({login_result.error_code}): "
        f"{login_result.error_msg}"
    )


def fetch_all_stock(
    day: date, login_retries: int = 3, retry_delay: float = 3.0
) -> list[dict[str, Any]]:
    """Fetch every security's basic information for ``day`` from Baostock."""
    _login(login_retries, retry_delay)

    try:
        result = bs.query_all_stock(day=day.isoformat())
        if result.error_code != "0":
            raise RuntimeError(
                f"Baostock query_all_stock failed ({result.error_code}): "
                f"{result.error_msg}"
            )

        records: list[dict[str, Any]] = []
        while result.next():
            row = result.get_row_data()
            records.append(
                {
                    "query_date": day,
                    "code": row[0],
                    "trade_status": int(row[1]) if row[1] else None,
                    "code_name": row[2] or None,
                }
            )
        return records
    finally:
        bs.logout()


def fetch_trade_dates(
    start_date: date | None = None,
    end_date: date | None = None,
    login_retries: int = 3,
    retry_delay: float = 3.0,
) -> list[dict[str, Any]]:
    """Fetch trading-day flags for a date range from Baostock."""
    _login(login_retries, retry_delay)

    try:
        result = bs.query_trade_dates(
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
        )
        if result.error_code != "0":
            raise RuntimeError(
                f"Baostock query_trade_dates failed ({result.error_code}): "
                f"{result.error_msg}"
            )

        records: list[dict[str, Any]] = []
        while result.next():
            row = result.get_row_data()
            records.append(
                {
                    "calendar_date": date.fromisoformat(row[0]),
                    "is_trading_day": int(row[1]),
                }
            )
        return records
    finally:
        bs.logout()
