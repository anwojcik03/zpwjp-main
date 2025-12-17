import yfinance as yf
from decorator_s import timer, cache
import pandas as pd
import streamlit as st
import requests


@timer
@cache
def fetch_stock(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end,auto_adjust=False)
    df = df.reset_index() 
    df.columns = df.columns.get_level_values("Price")
    df.columns.name = None
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

@st.cache_data(show_spinner=False)
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    html = requests.get(url, headers=headers).text
    tables = pd.read_html(html)
    df1 = tables[0]
    return df1["Symbol"].tolist()