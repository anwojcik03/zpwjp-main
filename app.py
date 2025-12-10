import streamlit as st
from data_fetcher import fetch_stock
from processing import compute_daily_returns, filter_date_range
from analysis import summary_stats, portfolio_calcs
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from plots import plot_price_interactive
from streamlit_searchbox import st_searchbox
from yahoo_fin import stock_info as si

tab1, tab2 = st.tabs(["Stats checker", "Portfolio Builder"])
@st.cache_data
def get_tickers_lib():
    return si.tickers_nasdaq()

tickers = get_tickers_lib()
start = st.sidebar.date_input("Start",pd.to_datetime("2024-11-01"))
end = st.sidebar.date_input("End")

def search_tickers(query: str):
        if not query:
            return []
        query = query.upper()
        return [t for t in tickers if t.startswith(query)]

with tab1:
    
    col1, col2 = st.columns(2)

    
    with col1:
        ticker = st_searchbox(
            search_tickers,
            label="Ticker",
            placeholder="type to search...",
            key="ticker_search1"
        )

    if ticker is None or ticker == "":
        st.warning("Please select a ticker")
    else:
        data = fetch_stock(ticker, str(start), str(end))
        data = compute_daily_returns(data)
        data = filter_date_range(data, start, end)

        st.subheader(f"{ticker}")
        st.plotly_chart(plot_price_interactive(data), use_container_width=True)

        stats = summary_stats(data)
        st.subheader("📊 Statystyki")
        st.dataframe(stats, hide_index=True)
        st.dataframe(data.sort_values("Date",ascending=False), hide_index=True)

with tab2:


    st.header("Portfolio Builder")
    
    selected = st.multiselect(
        "Select tickers for your portfolio:",
        options=tickers
    )

    st.divider()

    weights = {}
    if selected:
        st.subheader("Assign portfolio currency amount to each ticker:")
        for t in selected:
            weights[t] = st.number_input(
                label=f"{t}",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=0.1,
                key=f"weight_{t}"
            )
    
    if st.button("Calculate portfolio performance result"):
        if not selected:
            st.warning("Please select at least one ticker for your portfolio.")
        else:
            total_portfolio_value, profit_pct, portfolio_vol, portfolio_history = portfolio_calcs(selected,weights,start,end)
            st.subheader("Portfolio Results:")
            st.write(f"Initial portfolio value: {sum(weights.values()):.2f}")
            st.write(f"Total portfolio value after time period: {total_portfolio_value:.2f}")
            st.write(f"Profit: {profit_pct:.2f}%")
            st.write(f"Daily volatility: {portfolio_vol:.2f}%")
            if portfolio_history is not None:
                st.subheader("Portfolio value over time")
                st.line_chart(portfolio_history)
            else:
                st.warning("Unable to plot the portfolio – different trading days or missing data.")














    # # Session state to store selected tickers
    # if "portfolio_tickers" not in st.session_state:
    #     st.session_state.portfolio_tickers = [""]  # start with one empty search box


    # # --- Function to render all search boxes dynamically ---
    # def render_search_boxes():
    #     for i in range(len(st.session_state.portfolio_tickers)):
    #         selected = st_searchbox(
    #             search_tickers,
    #             key=f"ticker_box_{i}",
    #             placeholder="Type ticker...",
    #             label=f"Ticker {i+1}",
    #         )
    #         st.session_state.portfolio_tickers[i] = selected


    # render_search_boxes()
    # if st.button("➕ Add next ticker"):
    #     st.session_state.portfolio_tickers.append("")
    #     st.rerun()

    # st.divider()

    # # Show final list
    # clean_list = [t for t in st.session_state.portfolio_tickers if t not in (None, "", [])]

    # st.subheader("Selected tickers:")
    # st.write(clean_list)


