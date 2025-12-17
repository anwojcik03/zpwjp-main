import pandas as pd

def compute_daily_returns(df):
    df = df.copy()
    df["Return"] = df["Close"].pct_change()
    return df
