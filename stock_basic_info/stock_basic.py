"""Download Baostock daily securities and save them to the project DuckDB."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from stock_basic_info.baostock_client import fetch_all_stock
from stock_basic_info.stock_basic_repository import (
    DEFAULT_DATABASE,
    save_stock_basic_info,
)


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
    args = parser.parse_args()

    records = fetch_all_stock(args.date)
    count = save_stock_basic_info(records, args.database)
    print(f"Saved {count} securities for {args.date.isoformat()} to {args.database}")


if __name__ == "__main__":
    main()
