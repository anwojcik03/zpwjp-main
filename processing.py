import pandas as pd

def compute_daily_returns(df):
    df = df.copy()
    df["Return"] = df["Close"].pct_change()
    return df

def filter_date_range(df, start, end):
    if start is None or end is None:
        return df  # nie filtrujemy jeśli daty puste

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    df = df[(df["Date"] >= start) & (df["Date"] <= end)]
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df