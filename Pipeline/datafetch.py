import logging
import requests

API_URL = "https://open.er-api.com/v6/latest/USD"

HEADERS = {
    "User-Agent": "currency-pipeline/1.0",
    "Accept": "application/json",
}


def fetch_data():
    """Fetch latest USD exchange rates from open.er-api.com."""
    r = requests.get(API_URL, headers=HEADERS, timeout=30)
    logging.warning("API status: %s", r.status_code)
    r.raise_for_status()

    data = r.json()

    if data.get("result") != "success" or not data.get("rates"):
        raise ValueError(f"Bad API response. Keys: {list(data.keys())}")

    logging.warning("Got %d rates from open.er-api.com", len(data["rates"]))

    return {
        "base": data["base_code"],
        "timestamp": data["time_last_update_unix"],
        "rates": data["rates"],
        "source": "open.er-api.com",}