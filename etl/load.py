from datetime import date
from decimal import Decimal

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from etl.config import CREATE_TABLES_SQL, DATABASE_URL
from etl.logger import get_logger

logger = get_logger(__name__)


def create_db_engine(database_url: str = DATABASE_URL) -> Engine:
    return create_engine(database_url, future=True)


def ensure_schema(engine: Engine, ddl_path=CREATE_TABLES_SQL) -> None:
    """Create warehouse tables if they do not already exist."""
    ddl = ddl_path.read_text(encoding="utf-8")
    with engine.begin() as connection:
        connection.exec_driver_sql(ddl)
    logger.info("Warehouse schema is ready")


def _date_id(value: date) -> int:
    return int(pd.Timestamp(value).strftime("%Y%m%d"))


def _dimension_dates(events: pd.DataFrame) -> pd.DataFrame:
    dates = pd.DataFrame({"full_date": pd.to_datetime(events["event_date"]).dt.date})
    dates = dates.drop_duplicates().sort_values("full_date").reset_index(drop=True)
    dates["date_id"] = dates["full_date"].map(_date_id)
    date_values = pd.to_datetime(dates["full_date"])
    dates["date_year"] = date_values.dt.year
    dates["date_quarter"] = date_values.dt.quarter
    dates["date_month"] = date_values.dt.month
    dates["month_name"] = date_values.dt.month_name()
    dates["date_day"] = date_values.dt.day
    dates["day_name"] = date_values.dt.day_name()
    return dates


def upsert_customers(connection: Connection, events: pd.DataFrame) -> int:
    customers = (
        events[["customer_name"]]
        .drop_duplicates()
        .assign(customer_type="Regular")
        .to_dict("records")
    )

    if not customers:
        return 0

    connection.execute(
        text(
            """
            INSERT INTO dim_customer (customer_name, customer_type)
            VALUES (:customer_name, :customer_type)
            ON CONFLICT (customer_name) DO UPDATE
            SET customer_type = EXCLUDED.customer_type
            """
        ),
        customers,
    )
    return len(customers)


def upsert_services(connection: Connection, events: pd.DataFrame) -> int:
    services = (
        events[["service_category", "service_name"]]
        .drop_duplicates()
        .to_dict("records")
    )

    if not services:
        return 0

    connection.execute(
        text(
            """
            INSERT INTO dim_service (service_category, service_name)
            VALUES (:service_category, :service_name)
            ON CONFLICT (service_category, service_name) DO NOTHING
            """
        ),
        services,
    )
    return len(services)


def upsert_dates(connection: Connection, events: pd.DataFrame) -> int:
    dates = _dimension_dates(events).to_dict("records")

    if not dates:
        return 0

    connection.execute(
        text(
            """
            INSERT INTO dim_date (
                date_id,
                full_date,
                date_year,
                date_quarter,
                date_month,
                month_name,
                date_day,
                day_name
            )
            VALUES (
                :date_id,
                :full_date,
                :date_year,
                :date_quarter,
                :date_month,
                :month_name,
                :date_day,
                :day_name
            )
            ON CONFLICT (full_date) DO UPDATE
            SET
                date_year = EXCLUDED.date_year,
                date_quarter = EXCLUDED.date_quarter,
                date_month = EXCLUDED.date_month,
                month_name = EXCLUDED.month_name,
                date_day = EXCLUDED.date_day,
                day_name = EXCLUDED.day_name
            """
        ),
        dates,
    )
    return len(dates)


def _fetch_customer_map(connection: Connection) -> dict[str, int]:
    rows = connection.execute(
        text("SELECT customer_id, customer_name FROM dim_customer")
    ).mappings()
    return {row["customer_name"]: row["customer_id"] for row in rows}


def _fetch_service_map(connection: Connection) -> dict[tuple[str, str], int]:
    rows = connection.execute(
        text("SELECT service_id, service_category, service_name FROM dim_service")
    ).mappings()
    return {
        (row["service_category"], row["service_name"]): row["service_id"]
        for row in rows
    }


def _fetch_date_map(connection: Connection) -> dict[date, int]:
    rows = connection.execute(text("SELECT date_id, full_date FROM dim_date")).mappings()
    return {row["full_date"]: row["date_id"] for row in rows}


def upsert_fact_revenue(connection: Connection, events: pd.DataFrame) -> int:
    customer_map = _fetch_customer_map(connection)
    service_map = _fetch_service_map(connection)
    date_map = _fetch_date_map(connection)

    fact_records = []
    for row in events.itertuples(index=False):
        event_date = pd.Timestamp(row.event_date).date()
        fact_records.append(
            {
                "source_system": row.source_system,
                "source_record_id": str(row.source_record_id),
                "customer_id": customer_map[row.customer_name],
                "service_id": service_map[(row.service_category, row.service_name)],
                "date_id": date_map[event_date],
                "revenue": Decimal(str(row.revenue)),
            }
        )

    if not fact_records:
        return 0

    connection.execute(
        text(
            """
            INSERT INTO fact_revenue (
                source_system,
                source_record_id,
                customer_id,
                service_id,
                date_id,
                revenue
            )
            VALUES (
                :source_system,
                :source_record_id,
                :customer_id,
                :service_id,
                :date_id,
                :revenue
            )
            ON CONFLICT (source_system, source_record_id) DO UPDATE
            SET
                customer_id = EXCLUDED.customer_id,
                service_id = EXCLUDED.service_id,
                date_id = EXCLUDED.date_id,
                revenue = EXCLUDED.revenue,
                updated_at = NOW()
            """
        ),
        fact_records,
    )
    return len(fact_records)


def load_warehouse(events: pd.DataFrame, engine: Engine) -> dict[str, int]:
    """Load transformed events into the warehouse using idempotent upserts."""
    if events.empty:
        logger.info("No valid events to load")
        return {"customers": 0, "services": 0, "dates": 0, "facts": 0}

    with engine.begin() as connection:
        counts = {
            "customers": upsert_customers(connection, events),
            "services": upsert_services(connection, events),
            "dates": upsert_dates(connection, events),
            "facts": upsert_fact_revenue(connection, events),
        }

    logger.info("Load complete: %s", counts)
    return counts
