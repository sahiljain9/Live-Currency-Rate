# Pipeline/features.py


def calculate_daily_change(current_rate, previous_rate):
    """
    Feature 1: Daily Change %
    Percentage change in exchange rate compared to the previous day.
    Positive means the rate went up, negative means it went down.
    """
    if previous_rate == 0 or previous_rate is None:
        return 0.0
    return round(((current_rate - previous_rate) / previous_rate) * 100, 4)
