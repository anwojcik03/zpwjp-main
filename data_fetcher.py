import yfinance as yf
from decorator_s import timer, cache
import pandas as pd
#def fetch_stock(ticker: str, period="1mo", interval="1d"):
#    data = yf.download(ticker, period=period, interval=interval)
#    return data.reset_index()

@timer
@cache
def fetch_stock(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end)
    df = df.reset_index() 
    df.columns = df.columns.get_level_values("Price")
    df.columns.name = None
    df["Date"] = pd.to_datetime(df["Date"])
    return df