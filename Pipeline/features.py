# Pipeline/features.py
import numpy as np

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
