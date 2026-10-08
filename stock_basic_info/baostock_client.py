"""Baostock API client operations."""

from __future__ import annotations

from datetime import date
import time
from typing import Any, Iterable

import baostock as bs


NETWORK_ERROR_CODES = {"10002007"}

HISTORY_K_FREQUENCIES = ("d", "w", "m", "5", "15", "30", "60")

_HISTORY_K_FIELDS = {
    "d": (
        "date,code,open,high,low,close,preclose,volume,amount,"
        "adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST"
    ),
    "w": (
        "date,code,open,high,low,close,preclose,volume,amount,"
        "adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST"
    ),
    "m": (
        "date,code,open,high,low,close,preclose,volume,amount,"
        "adjustflag,turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST"
    ),
    "5": (
        "date,time,code,open,high,low,close,preclose,volume,amount,adjustflag,"
        "turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST"
    ),
    "15": (
        "date,time,code,open,high,low,close,preclose,volume,amount,adjustflag,"
        "turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST"
    ),
    "30": (
        "date,time,code,open,high,low,close,preclose,volume,amount,adjustflag,"
        "turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST"
    ),
    "60": (
        "date,time,code,open,high,low,close,preclose,volume,amount,adjustflag,"
        "turn,tradestatus,pctChg,peTTM,psTTM,pcfNcfTTM,pbMRQ,isST"
    ),
}


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


def _validate_history_k_args(
    code: str, frequency: str, adjustflag: str
) -> tuple[str, str]:
    if not code or not code.strip():
        raise ValueError("code must not be empty")

    normalized_frequency = str(frequency).lower()
    if normalized_frequency not in HISTORY_K_FREQUENCIES:
        choices = ", ".join(HISTORY_K_FREQUENCIES)
        raise ValueError(f"frequency must be one of: {choices}")

    normalized_adjustflag = str(adjustflag)
    if normalized_adjustflag not in {"1", "2", "3"}:
        raise ValueError("adjustflag must be one of: 1, 2, 3")
    return normalized_frequency, normalized_adjustflag


def _optional_float(value: str) -> float | None:
    return float(value) if value not in (None, "") else None


def _optional_int(value: str) -> int | None:
    return int(value) if value not in (None, "") else None


def _history_row_to_record(row: dict[str, str], frequency: str) -> dict[str, Any]:
    return {
        "trade_date": date.fromisoformat(row["date"]),
        # The API only returns time for minute frequencies. The empty string
        # gives the unified DuckDB table a non-null conflict key for d/w/m.
        "trade_time": row.get("time") or "",
        "code": row.get("code"),
        "frequency": frequency,
        "open": _optional_float(row.get("open")),
        "high": _optional_float(row.get("high")),
        "low": _optional_float(row.get("low")),
        "close": _optional_float(row.get("close")),
        "preclose": _optional_float(row.get("preclose")),
        "volume": _optional_int(row.get("volume")),
        "amount": _optional_float(row.get("amount")),
        "adjustflag": _optional_int(row.get("adjustflag")),
        "turn": _optional_float(row.get("turn")),
        "tradestatus": _optional_int(row.get("tradestatus")),
        "pct_chg": _optional_float(row.get("pctChg")),
        "pe_ttm": _optional_float(row.get("peTTM")),
        "ps_ttm": _optional_float(row.get("psTTM")),
        "pcf_ncf_ttm": _optional_float(row.get("pcfNcfTTM")),
        "pb_mrq": _optional_float(row.get("pbMRQ")),
        "is_st": _optional_int(row.get("isST")),
    }


def _query_history_k_data(
    code: str,
    start_date: date | None,
    end_date: date | None,
    frequency: str,
    adjustflag: str,
) -> list[dict[str, Any]]:
    fields = _HISTORY_K_FIELDS[frequency]
    result = bs.query_history_k_data_plus(
        code,
        fields,
        start_date=start_date.isoformat() if start_date else None,
        end_date=end_date.isoformat() if end_date else None,
        frequency=frequency,
        adjustflag=adjustflag,
    )
    if result.error_code != "0":
        raise RuntimeError(
            f"Baostock query_history_k_data_plus failed ({result.error_code}): "
            f"{result.error_msg}"
        )

    requested_fields = fields.split(",")
    result_fields = list(getattr(result, "fields", requested_fields))
    records: list[dict[str, Any]] = []
    while result.next():
        values = result.get_row_data()
        row = dict(zip(result_fields, values))
        records.append(_history_row_to_record(row, frequency))
    return records


def fetch_history_k_data(
    code: str,
    start_date: date | None = None,
    end_date: date | None = None,
    frequency: str = "d",
    adjustflag: str = "3",
    login_retries: int = 3,
    retry_delay: float = 3.0,
) -> list[dict[str, Any]]:
    """Fetch one frequency of historical A-share K-line data."""
    normalized_frequency, normalized_adjustflag = _validate_history_k_args(
        code, frequency, adjustflag
    )
    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date cannot be later than end_date")

    _login(login_retries, retry_delay)
    try:
        return _query_history_k_data(
            code,
            start_date,
            end_date,
            normalized_frequency,
            normalized_adjustflag,
        )
    finally:
        bs.logout()


def fetch_history_k_data_all(
    code: str,
    start_date: date | None = None,
    end_date: date | None = None,
    frequencies: Iterable[str] = HISTORY_K_FREQUENCIES,
    adjustflag: str = "3",
    login_retries: int = 3,
    retry_delay: float = 3.0,
) -> list[dict[str, Any]]:
    """Fetch all requested K-line frequencies in one Baostock session."""
    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date cannot be later than end_date")
    normalized_frequencies = [
        _validate_history_k_args(code, frequency, adjustflag)[0]
        for frequency in frequencies
    ]
    normalized_adjustflag = str(adjustflag)
    if not normalized_frequencies:
        return []

    _login(login_retries, retry_delay)
    try:
        records: list[dict[str, Any]] = []
        for frequency in normalized_frequencies:
            records.extend(
                _query_history_k_data(
                    code,
                    start_date,
                    end_date,
                    frequency,
                    normalized_adjustflag,
                )
            )
        return records
    finally:
        bs.logout()
