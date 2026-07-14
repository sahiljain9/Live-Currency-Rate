# loader.py

import os
import logging
from datetime import datetime, timezone

import mysql.connector
from dotenv import load_dotenv

from Pipeline.transform import transform_data

load_dotenv()  # local only; Azure uses App Settings

REQUIRED_VARS = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]

DATA_SOURCE = "open.er-api.com"

# INSERT IGNORE + unique key on (base, target, rate_timestamp) = idempotent
INSERT_QUERY = """
    INSERT IGNORE INTO currency_raw_rates
    (base_currency, target_currency, exchange_rate, rate_timestamp, fetched_at, source)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
# Connect to Azure MySQL using credentials from environment variables.
# Locally these come from the .env file; on Azure from App Settings.

def get_connection():
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {missing}")

    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        ssl_disabled=False,          # Azure MySQL requires SSL
        connection_timeout=30,
    )


def load_data():
    df = transform_data()

    row_count = 0 if df is None else len(df)
    logging.warning("transform_data() returned %d rows", row_count)

    if df is None or df.empty:
        raise ValueError("transform_data() returned an empty DataFrame — nothing to insert")

    current_time = datetime.now(timezone.utc)

    # numpy types -> native Python; mysql-connector rejects numpy.float64
    rows = [
        (
            str(r.base_currency),
            str(r.target_currency),
            float(r.exchange_rate),
            r.timestamp.to_pydatetime(),   # when the API published this rate
            current_time,                  # when we fetched it
            DATA_SOURCE,
        )
        for r in df.itertuples(index=False)
    ]

    conn = None
    try:
        conn = get_connection()
        logging.warning("Connected to database: %s", os.environ["DB_NAME"])

        cursor = conn.cursor()
        cursor.executemany(INSERT_QUERY, rows)
        inserted = cursor.rowcount
        conn.commit()

        skipped = len(rows) - inserted
        if skipped > 0:
            logging.warning("%d rows skipped as duplicates (already loaded)", skipped)

        cursor.execute("SELECT COUNT(*) FROM currency_raw_rates")
        total = cursor.fetchone()[0]
        logging.warning("Inserted %d rows. Table now has %d total.", inserted, total)

        cursor.close()
        return inserted

    except Exception:
        if conn:
            conn.rollback()
        logging.exception("Database insert failed")
        raise

    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_data()