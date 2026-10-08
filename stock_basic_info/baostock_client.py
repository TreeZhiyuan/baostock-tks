"""Baostock API client operations."""

from __future__ import annotations

from datetime import date
from typing import Any

import baostock as bs


def fetch_all_stock(day: date) -> list[dict[str, Any]]:
    """Fetch every security's basic information for ``day`` from Baostock."""
    login_result = bs.login()
    if login_result.error_code != "0":
        raise RuntimeError(
            f"Baostock login failed ({login_result.error_code}): "
            f"{login_result.error_msg}"
        )

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
