"""Download Baostock trading calendar data and save it to DuckDB."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from stock_basic_info.baostock_client import fetch_trade_dates
from stock_basic_info.database import DEFAULT_DATABASE
from stock_basic_info.trade_calendar_repository import save_trade_calendar


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch Baostock trading dates and save them to DuckDB."
    )
    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        help="first date in YYYY-MM-DD format (default: Baostock default)",
    )
    parser.add_argument(
        "--end-date",
        type=date.fromisoformat,
        help="last date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"DuckDB file (default: {DEFAULT_DATABASE})",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="login retries when the Baostock connection fails (default: 3)",
    )
    args = parser.parse_args()

    if args.start_date and args.end_date and args.start_date > args.end_date:
        parser.error("--start-date cannot be later than --end-date")

    try:
        records = fetch_trade_dates(
            args.start_date,
            args.end_date,
            login_retries=args.retries,
        )
    except RuntimeError as error:
        parser.exit(1, f"错误：{error}\n")

    count = save_trade_calendar(records, args.database)
    print(f"Saved {count} calendar dates to {args.database}")


if __name__ == "__main__":
    main()
