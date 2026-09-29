"""
I/O helpers for exporting and importing datasets in CSV, Parquet, and JSON formats.
"""

from pathlib import Path
import pandas as pd


def save_dataframe(
    df: pd.DataFrame,
    filepath: str | Path,
    export_parquet: bool = True,
    export_csv: bool = True,
) -> None:
    """
    Save DataFrame to CSV and/or Parquet formats, ensuring parent directories exist.
    
    Args:
        df: Pandas DataFrame to save.
        filepath: Target base filepath (without extension or with .csv/.parquet).
        export_parquet: Whether to save parquet version.
        export_csv: Whether to save csv version.
    """
    path = Path(filepath)
    base_stem = path.with_suffix("")
    base_stem.parent.mkdir(parents=True, exist_ok=True)

    if export_parquet:
        parquet_file = base_stem.with_suffix(".parquet")
        df.to_parquet(parquet_file, index=False, engine="pyarrow")

    if export_csv:
        csv_file = base_stem.with_suffix(".csv")
        df.to_csv(csv_file, index=False)


def load_dataframe(filepath: str | Path) -> pd.DataFrame:
    """
    Load DataFrame from Parquet or CSV.
    
    Args:
        filepath: Filepath to load.
        
    Returns:
        Loaded pandas DataFrame.
    """
    path = Path(filepath)
    if path.suffix == ".parquet" or (path.with_suffix(".parquet").exists()):
        target = path if path.suffix == ".parquet" else path.with_suffix(".parquet")
        return pd.read_parquet(target)
    elif path.suffix == ".csv" or (path.with_suffix(".csv").exists()):
        target = path if path.suffix == ".csv" else path.with_suffix(".csv")
        return pd.read_csv(target)
    else:
        raise FileNotFoundError(f"File not found with .parquet or .csv: {filepath}")
