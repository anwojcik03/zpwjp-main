import pandas as pd
import warnings
from processing import compute_daily_returns, filter_date_range
from data_fetcher import fetch_stock
import numpy as np
def summary_stats(df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df = df.sort_values("Date")

        # if df.empty:
        #     return pd.DataFrame(
        #         [
        #             ("Mean daily return", None),
        #             ("Volatility", None),
        #             ("Full return", None),
        #             ("Min price", None),
        #             ("Max price", None)
        #         ],
        #         columns=["Metric", "Value"]
        #     )

        # Calculate full return safely
        first = df["Close"].iloc[0]
        last = df["Close"].iloc[-1]
        full_return = (last / first) - 1

        stats = {
            "Mean daily return": f'{df["Return"].mean() * 100:.2f}%',
            "Volatility": f'{df["Return"].std() * 100:.2f}%',
            "Full return": f'{full_return * 100:.2f}%',
            "Min price": f'{df["Close"].min():.2f}',
            "Max price": f'{df["Close"].max():.2f}'
        }

        return pd.DataFrame(
            [(k, v) for k, v in stats.items()],
            columns=["Metric", "Value"]
        )
    
def portfolio_calcs(tickers, weights, start, end):
    portfolio_df = None

    for ticker in tickers:
        data = fetch_stock(ticker, str(start), str(end))
        data = filter_date_range(data, start, end)

        data = data[["Date", "Close"]].copy()
        data.rename(columns={"Close": ticker}, inplace=True)

        # pierwszy ticker → ustawiamy bazowy df
        if portfolio_df is None:
            portfolio_df = data
        else:
            # INNER JOIN po Date
            portfolio_df = portfolio_df.merge(data, on="Date", how="inner")

    # ustawiamy Date jako index
    portfolio_df.set_index("Date", inplace=True)

    # przeliczamy wartości i sumę portfela
    for ticker in tickers:
        portfolio_df[ticker] = portfolio_df[ticker] / portfolio_df[ticker].iloc[0] * weights[ticker]

    portfolio_df["Portfolio"] = portfolio_df[tickers].sum(axis=1)
    portfolio_df["Return"] = portfolio_df["Portfolio"].pct_change()

    # wyniki
    first = portfolio_df["Portfolio"].iloc[0]
    last = portfolio_df["Portfolio"].iloc[-1]

    profit_pct = (last / first - 1) * 100
    volatility_daily = portfolio_df["Return"].std() * 100

    return last, profit_pct, volatility_daily, portfolio_df["Portfolio"]




