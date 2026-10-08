"""Download Baostock daily securities and save them to the project DuckDB."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from stock_basic_info.baostock_client import fetch_all_stock
from stock_basic_info.database import DEFAULT_DATABASE
from stock_basic_info.stock_basic_repository import save_stock_basic_info


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch Baostock securities for a date and save them to DuckDB."
    )
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=date.today(),
        help="query date in YYYY-MM-DD format (default: today)",
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

    try:
        records = fetch_all_stock(args.date, login_retries=args.retries)
    except RuntimeError as error:
        parser.exit(1, f"错误：{error}\n")

    count = save_stock_basic_info(records, args.database)
    print(
        f"Saved {count} securities for {args.date.isoformat()} to {args.database}"
    )


if __name__ == "__main__":
    main()
