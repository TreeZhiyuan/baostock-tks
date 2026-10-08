"""Shared project paths for DuckDB persistence."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "duckdb" / "sharp_market.duckdb"
