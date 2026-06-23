import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DATABASE_DIR = ROOT_DIR / "database"
LOG_DIR = ROOT_DIR / "logs"

load_dotenv(ROOT_DIR / ".env")

CREATE_TABLES_SQL = DATABASE_DIR / "create_tables.sql"
ERROR_LOG_PATH = LOG_DIR / "error_log.csv"
ETL_LOG_PATH = LOG_DIR / "etl.log"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://admin:admin@localhost:5432/hotel_dw",
)

# The restaurant, spa, and casino sample files do not contain business dates.
# If future source files add date columns, transform.py will use them first.
DEFAULT_EVENT_DATE = os.getenv("DEFAULT_EVENT_DATE", "2025-01-01")

SOURCE_CONFIG = {
    "bookings": {
        "file_name": "bookings.csv",
        "id_column": "booking_id",
        "revenue_column": "room_price",
        "service_category": "Hotel",
        "service_name_column": "room_type",
        "event_date_column": "check_in",
        "date_columns": ["check_in", "check_out"],
    },
    "restaurant": {
        "file_name": "restaurant.csv",
        "id_column": "order_id",
        "revenue_column": "amount",
        "service_category": "Restaurant",
        "service_name_column": "item",
        "event_date_candidates": ["order_date", "transaction_date", "date"],
    },
    "spa": {
        "file_name": "spa.csv",
        "id_column": "spa_id",
        "revenue_column": "amount",
        "service_category": "Spa",
        "service_name_column": "service",
        "event_date_candidates": ["service_date", "transaction_date", "date"],
    },
    "casino": {
        "file_name": "casino.csv",
        "id_column": "transaction_id",
        "revenue_column": "amount",
        "service_category": "Casino",
        "service_name_column": "game",
        "event_date_candidates": ["transaction_date", "gaming_date", "date"],
    },
}
