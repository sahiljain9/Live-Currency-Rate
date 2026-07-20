# Pipeline/features.py
import numpy as np
from Pipeline.loader import get_connection
from datetime import datetime, timezone

def calculate_daily_change(current_rate, previous_rate):
    """
    Feature 1: Daily Change %
    Percentage change in exchange rate compared to the previous day.
    Positive means the rate went up, negative means it went down.
    """
    if previous_rate == 0 or previous_rate is None:
        return 0.0
    return round(((current_rate - previous_rate) / previous_rate) * 100, 4)

def calculate_weekly_change(current_rate, week_ago_rate):
    """
    Feature 2: Weekly Change %
    Percentage change in exchange rate compared to 7 days ago.
    """
    if week_ago_rate == 0 or week_ago_rate is None:
        return 0.0
    return round(((current_rate - week_ago_rate) / week_ago_rate) * 100, 4)

def calculate_volatility(rates):
    """
    Feature 3: Volatility Score
    Standard deviation of recent rates.
    """
    if not rates or len(rates) < 2:
        return 0.0
    return round(float(np.std(rates)), 6)

def detect_anomaly(rates, threshold=2.0):
    """
    Feature 4: Anomaly Detection
    Flags the latest rate as 'Anomaly' if it deviates significantly
    from the recent average, otherwise 'Normal'.
    """
    if not rates or len(rates) < 2:
        return "Normal"
    mean = np.mean(rates)
    std = np.std(rates)
    if std == 0:
        return "Normal"
    z = (rates[0] - mean) / std
    return "Anomaly" if abs(z) > threshold else "Normal"

def calculate_moving_average(rates):
    """
    Feature 5: Moving Average
    Average of recent rates to show the overall level.
    """
    if not rates:
        return 0.0
    return round(sum(rates) / len(rates), 6)

def get_recent_rates(target_currency, limit=7):
    """
    Fetch recent rates for ONE currency from the raw table, newest first.
    Called in a loop (one currency at a time) to process all currencies.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT exchange_rate FROM currency_raw_rates
        WHERE target_currency = %s
        ORDER BY rate_timestamp DESC
        LIMIT %s
    """, (target_currency, limit))
    rates = [float(r[0]) for r in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rates

def get_all_currencies():
    """Get list of all distinct currencies from the raw table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT target_currency FROM currency_raw_rates")
    currencies = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return currencies

def save_features():
    """Compute all five features for every currency and save to currency_features."""
    conn = get_connection()
    cursor = conn.cursor()
    computed_at = datetime.now(timezone.utc)

    currencies = get_all_currencies()
    saved = 0

    for currency in currencies:
        rates = get_recent_rates(currency)
        if len(rates) < 2:
            continue

        current = rates[0]
        previous = rates[1]
        week_ago = rates[-1]

        cursor.execute("""
            INSERT INTO currency_features
            (target_currency, current_rate, daily_change_pct, weekly_change_pct,
             volatility, anomaly_flag, moving_average, computed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            currency,
            current,
            calculate_daily_change(current, previous),
            calculate_weekly_change(current, week_ago),
            calculate_volatility(rates),
            detect_anomaly(rates),
            calculate_moving_average(rates),
            computed_at,
        ))
        saved += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved features for {saved} currencies at {computed_at}")
    return saved


if __name__ == "__main__":
    save_features()
