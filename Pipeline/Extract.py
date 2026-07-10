import logging
import pandas as pd
from Pipeline.datafetch import fetch_data


def extract_data():
    data = fetch_data()

    if not data:
        logging.error("fetch_data() returned empty/None")
        return pd.DataFrame()

    df = pd.DataFrame([
        {
            "base_currency": data["base"],
            "target_currency": currency,
            "exchange_rate": rate,
            "timestamp": data["timestamp"],
        }
        for currency, rate in data["rates"].items()
    ])

    logging.warning("extract_data() built %d rows", len(df))
    return df