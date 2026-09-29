"""
DuckDB Database connection and query execution helper.
"""

from pathlib import Path
from typing import Optional
import duckdb
import pandas as pd


class DatabaseManager:
    """Manages DuckDB connection, table registration, and SQL execution."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path and db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self.con = duckdb.connect(db_path)
        else:
            self.con = duckdb.connect(":memory:")

    def register_dataframe(self, name: str, df: pd.DataFrame) -> None:
        """Register a pandas DataFrame as a table/view in DuckDB."""
        self.con.register(name, df)

    def execute(self, query: str) -> duckdb.DuckDBPyConnection:
        """Execute a raw SQL query."""
        return self.con.execute(query)

    def query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a Pandas DataFrame."""
        return self.con.execute(query).df()

    def execute_script(self, script_path: str | Path) -> None:
        """Execute all SQL statements in a file."""
        with open(script_path, "r", encoding="utf-8") as f:
            sql = f.read()
        self.con.execute(sql)

    def close(self) -> None:
        """Close connection."""
        self.con.close()
