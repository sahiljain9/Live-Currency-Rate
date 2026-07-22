# tests/test_integration.py

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd

from Pipeline.loader import get_connection
from Pipeline.features import (
    get_all_currencies,
    get_recent_rates,
    calculate_daily_change,
    calculate_volatility,
)


#  Backend and database 

def test_database_returns_currencies():
    """Backend connects to Azure MySQL and fetches the currency list."""
    currencies = get_all_currencies()
    assert len(currencies) > 0
    assert isinstance(currencies[0], str)


def test_database_returns_rates():
    """Backend fetches real exchange rates for a currency from the database."""
    currencies = get_all_currencies()
    rates = get_recent_rates(currencies[0])
    assert len(rates) > 0
    assert all(isinstance(r, float) for r in rates)


def test_end_to_end_feature_computation():
    """Full flow: fetch rates from database and compute features on real data."""
    currencies = get_all_currencies()
    rates = get_recent_rates(currencies[0])

    if len(rates) >= 2:
        daily = calculate_daily_change(rates[0], rates[1])
        volatility = calculate_volatility(rates)

        assert isinstance(daily, float)
        assert isinstance(volatility, float)
        assert volatility >= 0


#  Frontend and backend 

def test_dashboard_loads_features_from_database():
    """Frontend query: the dashboard reads computed features from the database."""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT target_currency, current_rate, daily_change_pct,
               volatility, anomaly_flag, moving_average, computed_at
        FROM currency_features
        WHERE computed_at = (SELECT MAX(computed_at) FROM currency_features)
    """, conn)
    conn.close()

    assert not df.empty
    assert "target_currency" in df.columns
    assert "volatility" in df.columns


def test_frontend_backend_end_to_end():
    """Backend writes features to the database and the frontend reads them back."""
    currencies = get_all_currencies()
    assert len(currencies) > 0

    conn = get_connection()
    df = pd.read_sql("SELECT DISTINCT target_currency FROM currency_features", conn)
    conn.close()

    dashboard_currencies = set(df["target_currency"])
    assert len(dashboard_currencies) > 0
    assert dashboard_currencies.issubset(set(currencies))