import logging
import pandas as pd
from Pipeline.Extract import extract_data


def transform_data():
    df = extract_data()

    if df.empty:
        logging.error("extract_data() returned empty DataFrame")
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    logging.warning("transform_data() produced %d rows", len(df))

    return df