from collections.abc import Iterable

import pandas as pd

from etl.config import ERROR_LOG_PATH, SOURCE_CONFIG
from etl.logger import get_logger

logger = get_logger(__name__)


def _append_reason(
    reasons: pd.Series,
    mask: pd.Series,
    reason: str,
) -> None:
    for index in reasons.index[mask.fillna(False)]:
        reasons.at[index].append(reason)


def _missing_or_blank(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().eq("")


def _column_exists(df: pd.DataFrame, column: str) -> bool:
    return column in df.columns


def validate_source(source_name: str, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate a source DataFrame and return valid and invalid records."""
    config = SOURCE_CONFIG[source_name]
    working = df.copy()
    reasons = pd.Series([[] for _ in range(len(working))], index=working.index)

    if not _column_exists(working, "customer_name"):
        raise ValueError(f"{source_name} is missing required column: customer_name")

    id_column = config["id_column"]
    revenue_column = config["revenue_column"]

    if not _column_exists(working, id_column):
        raise ValueError(f"{source_name} is missing required column: {id_column}")

    if not _column_exists(working, revenue_column):
        raise ValueError(f"{source_name} is missing required column: {revenue_column}")

    _append_reason(
        reasons,
        _missing_or_blank(working["customer_name"]),
        "missing_customer_name",
    )
    _append_reason(reasons, _missing_or_blank(working[id_column]), "missing_source_record_id")

    revenue = pd.to_numeric(working[revenue_column], errors="coerce")
    _append_reason(reasons, revenue.isna(), "missing_or_invalid_revenue")
    _append_reason(reasons, revenue < 0, "negative_revenue")

    duplicate_rows = working.duplicated(keep="first")
    _append_reason(reasons, duplicate_rows, "duplicate_row")

    duplicate_source_ids = working[id_column].duplicated(keep="first")
    _append_reason(reasons, duplicate_source_ids, "duplicate_source_record_id")

    if source_name == "bookings":
        for date_column in config["date_columns"]:
            if not _column_exists(working, date_column):
                raise ValueError(f"{source_name} is missing required column: {date_column}")

        check_in = pd.to_datetime(working["check_in"], errors="coerce")
        check_out = pd.to_datetime(working["check_out"], errors="coerce")

        _append_reason(
            reasons,
            check_in.isna() | check_out.isna(),
            "missing_or_invalid_booking_date",
        )
        _append_reason(
            reasons,
            check_out < check_in,
            "check_out_earlier_than_check_in",
        )

    has_errors = reasons.map(bool)
    valid_records = working.loc[~has_errors].copy()
    invalid_records = working.loc[has_errors].copy()

    if not invalid_records.empty:
        invalid_records.insert(0, "source_row_number", invalid_records.index + 2)
        invalid_records.insert(0, "source_system", source_name)
        invalid_records.insert(
            2,
            "validation_errors",
            reasons.loc[has_errors].map(lambda items: "|".join(items)),
        )

    logger.info(
        "Validated %s: %s valid, %s invalid",
        source_name,
        len(valid_records),
        len(invalid_records),
    )
    return valid_records, invalid_records


def write_error_log(
    invalid_frames: Iterable[pd.DataFrame],
    error_log_path=ERROR_LOG_PATH,
) -> pd.DataFrame:
    """Write invalid rows for the current ETL run."""
    error_log_path.parent.mkdir(parents=True, exist_ok=True)
    invalid_frames = [frame for frame in invalid_frames if not frame.empty]

    if invalid_frames:
        error_log = pd.concat(invalid_frames, ignore_index=True, sort=False)
    else:
        error_log = pd.DataFrame(
            columns=["source_system", "source_row_number", "validation_errors"]
        )

    error_log.to_csv(error_log_path, index=False)
    logger.info("Wrote %s invalid records to %s", len(error_log), error_log_path)
    return error_log


def validate_sources(
    sources: dict[str, pd.DataFrame],
    error_log_path=ERROR_LOG_PATH,
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Validate all extracted sources and persist invalid records."""
    valid_sources = {}
    invalid_frames = []

    for source_name, df in sources.items():
        valid, invalid = validate_source(source_name, df)
        valid_sources[source_name] = valid
        invalid_frames.append(invalid)

    error_log = write_error_log(invalid_frames, error_log_path)
    return valid_sources, error_log
