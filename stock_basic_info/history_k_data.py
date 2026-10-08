"""Download Baostock historical A-share K-lines into DuckDB."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from stock_basic_info.baostock_client import (
    HISTORY_K_FREQUENCIES,
    fetch_history_k_data_all,
)
from stock_basic_info.database import DEFAULT_DATABASE
from stock_basic_info.history_k_data_repository import save_history_k_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch Baostock historical A-share K-lines and save them to DuckDB."
    )
    parser.add_argument(
        "--code",
        action="append",
        required=True,
        help="security code such as sh.600000; repeat for multiple securities",
    )
    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        help="first date in YYYY-MM-DD format (default: Baostock default)",
    )
    parser.add_argument(
        "--end-date",
        type=date.fromisoformat,
        help="last date in YYYY-MM-DD format (default: latest trading day)",
    )
    parser.add_argument(
        "--frequency",
        dest="frequencies",
        choices=HISTORY_K_FREQUENCIES,
        action="append",
        help="K-line frequency; repeat to select several (default: all seven)",
    )
    parser.add_argument(
        "--adjustflag",
        choices=("1", "2", "3"),
        default="3",
        help="1后复权、2前复权、3不复权 (default: 3)",
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

    frequencies = args.frequencies or HISTORY_K_FREQUENCIES
    total = 0
    try:
        for code in args.code:
            records = fetch_history_k_data_all(
                code,
                start_date=args.start_date,
                end_date=args.end_date,
                frequencies=frequencies,
                adjustflag=args.adjustflag,
                login_retries=args.retries,
            )
            total += save_history_k_data(records, args.database)
    except (RuntimeError, ValueError) as error:
        parser.exit(1, f"错误：{error}\n")

    print(
        f"Saved {total} K-line records for {len(args.code)} security(ies) "
        f"at frequencies {', '.join(frequencies)} to {args.database}"
    )


if __name__ == "__main__":
    main()
