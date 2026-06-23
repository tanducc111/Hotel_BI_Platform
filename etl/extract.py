from pathlib import Path

import pandas as pd

from etl.config import DATA_DIR, SOURCE_CONFIG
from etl.logger import get_logger

logger = get_logger(__name__)


def read_csv_source(source_name: str, file_path: Path) -> pd.DataFrame:
    """Read one CSV source and normalize column names."""
    if not file_path.exists():
        raise FileNotFoundError(f"Missing source file for {source_name}: {file_path}")

    df = pd.read_csv(file_path, skip_blank_lines=True)
    df.columns = [column.strip() for column in df.columns]
    logger.info("Extracted %s rows from %s", len(df), file_path.name)
    return df


def extract_sources(data_dir: Path = DATA_DIR) -> dict[str, pd.DataFrame]:
    """Extract all configured source CSVs."""
    extracted = {}

    for source_name, config in SOURCE_CONFIG.items():
        file_path = data_dir / config["file_name"]
        extracted[source_name] = read_csv_source(source_name, file_path)

    return extracted
