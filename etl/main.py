import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from etl.extract import extract_sources
from etl.load import create_db_engine, ensure_schema, load_warehouse
from etl.logger import get_logger
from etl.transform import transform_sources
from etl.validate import validate_sources

logger = get_logger(__name__)


def run_etl() -> dict[str, int]:
    """Run the complete Extract -> Validate -> Transform -> Load pipeline."""
    logger.info("Starting hotel BI ETL pipeline")

    raw_sources = extract_sources()
    valid_sources, error_log = validate_sources(raw_sources)
    revenue_events = transform_sources(valid_sources)

    engine = create_db_engine()
    ensure_schema(engine)
    load_counts = load_warehouse(revenue_events, engine)

    logger.info(
        "ETL finished: %s valid events, %s invalid records",
        len(revenue_events),
        len(error_log),
    )
    return load_counts


if __name__ == "__main__":
    run_etl()
