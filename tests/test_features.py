# tests/test_features.py

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pipeline.features import (
    calculate_daily_change,
    calculate_weekly_change,
    calculate_volatility,
    detect_anomaly,
    calculate_moving_average,
)


# Feature 1: Daily Change
def test_daily_change_increase():
    assert calculate_daily_change(110, 100) == 10.0

def test_daily_change_decrease():
    assert calculate_daily_change(90, 100) == -10.0

def test_daily_change_zero_previous():
    assert calculate_daily_change(100, 0) == 0.0


# Feature 2: Weekly Change
def test_weekly_change_increase():
    assert calculate_weekly_change(107, 100) == 7.0

def test_weekly_change_zero():
    assert calculate_weekly_change(100, 0) == 0.0


# Feature 3: Volatility
def test_volatility_high():
    assert calculate_volatility([10, 100, 200, 300]) > 50

def test_volatility_empty():
    assert calculate_volatility([]) == 0.0

def test_volatility_single():
    assert calculate_volatility([50]) == 0.0


# Feature 4: Anomaly
def test_anomaly_normal():
    assert detect_anomaly([100, 100, 100, 100]) == "Normal"

def test_anomaly_detected():
    assert detect_anomaly([200, 100, 100, 100, 100, 100, 100]) == "Anomaly"

def test_anomaly_empty():
    assert detect_anomaly([]) == "Normal"


# Feature 5: Moving Average
def test_moving_average_basic():
    assert calculate_moving_average([10, 20, 30]) == 20.0

def test_moving_average_empty():
    assert calculate_moving_average([]) == 0.0