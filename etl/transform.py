import pandas as pd

from etl.config import DEFAULT_EVENT_DATE, SOURCE_CONFIG
from etl.logger import get_logger

logger = get_logger(__name__)


def _clean_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.replace(r"\s+", " ", regex=True)


def _resolve_event_date(
    source_name: str,
    df: pd.DataFrame,
    default_event_date: str,
) -> pd.Series:
    config = SOURCE_CONFIG[source_name]

    if "event_date_column" in config:
        return pd.to_datetime(df[config["event_date_column"]], errors="coerce").dt.date

    for candidate in config.get("event_date_candidates", []):
        if candidate in df.columns:
            return pd.to_datetime(df[candidate], errors="coerce").dt.date

    return pd.Series(
        pd.to_datetime(default_event_date).date(),
        index=df.index,
        dtype="object",
    )


def transform_source(
    source_name: str,
    df: pd.DataFrame,
    default_event_date: str = DEFAULT_EVENT_DATE,
) -> pd.DataFrame:
    """Transform one validated source into standardized revenue events."""
    config = SOURCE_CONFIG[source_name]
    service_name_column = config["service_name_column"]

    events = pd.DataFrame(index=df.index)
    events["source_system"] = source_name
    events["source_record_id"] = _clean_text(df[config["id_column"]])
    events["customer_name"] = _clean_text(df["customer_name"])
    events["service_category"] = config["service_category"]
    events["service_name"] = _clean_text(df[service_name_column]).replace("", config["service_category"])
    events["event_date"] = _resolve_event_date(source_name, df, default_event_date)
    events["revenue"] = pd.to_numeric(df[config["revenue_column"]], errors="coerce").round(2)

    return events


def transform_sources(
    valid_sources: dict[str, pd.DataFrame],
    default_event_date: str = DEFAULT_EVENT_DATE,
) -> pd.DataFrame:
    """Transform validated source frames into one warehouse-ready event table."""
    event_frames = [
        transform_source(source_name, df, default_event_date)
        for source_name, df in valid_sources.items()
        if not df.empty
    ]

    if not event_frames:
        return pd.DataFrame(
            columns=[
                "source_system",
                "source_record_id",
                "customer_name",
                "service_category",
                "service_name",
                "event_date",
                "revenue",
            ]
        )

    events = pd.concat(event_frames, ignore_index=True)
    events = events.drop_duplicates(
        subset=["source_system", "source_record_id"],
        keep="last",
    )
    events = events.sort_values(["event_date", "source_system", "source_record_id"])
    events = events.reset_index(drop=True)

    logger.info("Transformed %s validated records into revenue events", len(events))
    return events
