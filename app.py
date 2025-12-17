import streamlit as st
from data_fetcher import fetch_stock, get_sp500_tickers
from processing import compute_daily_returns
from analysis import summary_stats, portfolio_calcs
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from plots import plot_price_interactive
from streamlit_searchbox import st_searchbox
from clustering import compute_features
import plotly.express as px
import requests
import matplotlib.cm as cm
from sklearn.decomposition import PCA 
import plotly.express as px
from sklearn.preprocessing import StandardScaler 
from sklearn.cluster import KMeans 

today = datetime.date.today()
max_past_date_start = today - datetime.timedelta(days=6 * 365)
max_past_date_end = today - datetime.timedelta(days=2 * 365)

tab1, tab2, tab3 = st.tabs(["Stats checker", "Clustering", "Portfolio Builder"])
tickers = get_sp500_tickers()
start = st.sidebar.date_input("Start",pd.to_datetime("2024-11-01"), min_value=max_past_date_start, max_value=today)
end = st.sidebar.date_input("End", min_value=start, max_value=today)

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
        st.subheader(f"{ticker}")
        st.plotly_chart(plot_price_interactive(data),use_container_width=True)
        stats = summary_stats(data)
        st.subheader(" Statystyki")
        st.dataframe(stats, hide_index=True)
        st.dataframe(data.sort_values("Date",ascending=False), hide_index=True)




with tab2:
    st.header("Stock Clustering")
    tickers_selected = st.multiselect("Select tickers for clustering:", options=tickers, default=tickers[:10]) 
    
    feature_options = {
        "Mean daily return": "MeanReturn",
        "Volatility": "Volatility",
        "Full return": "FullReturn",
        "Max drawdown": "MaxDrawdown",
        "Correlation to SPY": "CorrSPY"
    }
    
    selected_features_labels = st.multiselect(
        "Select features:",
        options=list(feature_options.keys()),
        default=["Mean daily return", "Volatility", "Full return"]
    )
    
    if "Mean daily return" in selected_features_labels and "Full return" in selected_features_labels:
        st.warning("Nie możesz wybrać jednocześnie 'Mean daily return' i 'Full return'. Wybierz tylko jedną z nich.")
        run_clustering = False
    else:
        run_clustering = True

    selected_features = [feature_options[x] for x in selected_features_labels]
    n_clusters = st.slider("Number of clusters:", 2, 10, 3)

    if st.button("Run clustering") and run_clustering:
        if len(tickers_selected) < n_clusters:
            st.error("Number of tickers must be >= number of clusters")
        else:
            st.subheader("Computed features")
            
            df_feat = compute_features(tickers_selected, start, end)
            st.dataframe(df_feat)
            
            
            from clustering import run_clustering_pipeline
            
            
            df_feat = run_clustering_pipeline(df_feat, selected_features, n_clusters)
            

            n = df_feat["Cluster"].nunique()
            reds = cm.get_cmap("Reds", n)
            cluster_list = sorted(df_feat["Cluster"].unique())
            color_map = {cluster_list[i]: f'rgb({int(reds(i)[0]*255)}, {int(reds(i)[1]*255)}, {int(reds(i)[2]*255)})' 
                         for i in range(n)}

            
            X_features = df_feat[selected_features]
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_features) 
            
            n_features = X_features.shape[1]

            if n_features >= 3:
                pca = PCA(n_components=3)
                pcs = pca.fit_transform(X_scaled)
                df_feat["PC1"] = pcs[:, 0]
                df_feat["PC2"] = pcs[:, 1]
                df_feat["PC3"] = pcs[:, 2]

                st.subheader("PCA 2D")
                fig2d = px.scatter(
                    df_feat, x="PC1", y="PC2", color="Cluster",
                    color_discrete_map=color_map, hover_data=["Ticker"]
                )
                st.plotly_chart(fig2d,use_container_width=True)

                st.subheader("PCA 3D")
                fig3d = px.scatter_3d(
                    df_feat, x="PC1", y="PC2", z="PC3", color="Cluster",
                    color_discrete_map=color_map, hover_data=["Ticker"]
                )
                st.plotly_chart(fig3d, use_container_width=True)

            else:
                pca = PCA(n_components=2)
                pcs = pca.fit_transform(X_scaled)
                df_feat["PC1"] = pcs[:, 0]
                df_feat["PC2"] = pcs[:, 1]

                st.subheader("PCA 2D")
                fig2d = px.scatter(
                    df_feat, x="PC1", y="PC2", color="Cluster",
                    color_discrete_map=color_map, hover_data=["Ticker"]
                )
                st.plotly_chart(fig2d, use_container_width=True)
                
                st.subheader(" KMeans plot ")
                fig_simple = px.scatter(
                    df_feat, x=selected_features[0], y=selected_features[1],
                    color="Cluster", color_discrete_map=color_map, hover_data=["Ticker"]
                )
                st.plotly_chart(fig_simple, use_container_width=True)

            st.subheader("Tickers and pointed clusters ")
            st.dataframe(df_feat[["Ticker", "Cluster"]].sort_values("Cluster").reset_index(drop=True))



with tab3:

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
