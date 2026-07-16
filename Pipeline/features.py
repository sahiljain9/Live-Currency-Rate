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

def calculate_weekly_change(current_rate, week_ago_rate):
    """
    Feature 2: Weekly Change %
    Percentage change in exchange rate compared to 7 days ago.
    """
    if week_ago_rate == 0 or week_ago_rate is None:
        return 0.0
    return round(((current_rate - week_ago_rate) / week_ago_rate) * 100, 4)
