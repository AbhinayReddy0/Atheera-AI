import pandas as pd

def run_forecast(df):
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=30),
        "forecast": [100 + i for i in range(30)]
    })
