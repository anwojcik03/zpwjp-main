import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from data_fetcher import fetch_stock
from processing import compute_daily_returns
import functools


def compute_features(tickers, start, end):
    rows = []
    
    spy = fetch_stock("SPY", str(start), str(end))
    spy = compute_daily_returns(spy)

    for t in tickers:
        df = fetch_stock(t, str(start), str(end))
        df = compute_daily_returns(df)

        if df.empty:
            continue

        mean_ret = df["Return"].mean()
        vol = df["Return"].std()
        full_return = (df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1
        max_dd = ((df["Close"] / df["Close"].cummax()) - 1).min()

        merged = pd.merge(df[["Date", "Return"]],
                          spy[["Date", "Return"]],
                          on="Date", suffixes=("", "_SPY"))

        corr_spy = merged["Return"].corr(merged["Return_SPY"])
        rows.append([t, mean_ret, vol, full_return, max_dd, corr_spy])

    df_feat = pd.DataFrame(rows, columns=[
        "Ticker", "MeanReturn", "Volatility", "FullReturn", "MaxDrawdown", "CorrSPY"
    ])
    return df_feat



def filter_features(df, features_list):
    
    return df[features_list].copy()

def scale_data(df):
   
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
   
    return scaled_data

def perform_clustering(data_matrix, n_clusters, random_state=42):
    
    km = KMeans(n_clusters=n_clusters, random_state=random_state)
    clusters = km.fit_predict(data_matrix)
    return clusters

def compose(*functions):
   
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions)


def run_clustering_pipeline(df_input, selected_features, n_clusters):
   
    step3 = functools.partial(perform_clustering, n_clusters=n_clusters)
    
    
    step2 = scale_data
    
    
    step1 = functools.partial(filter_features, features_list=selected_features)
    
    
    pipeline = compose(step3, step2, step1)
    
    
    cluster_labels = pipeline(df_input)
    
    
    df_result = df_input.copy()
    df_result["Cluster"] = (cluster_labels + 1).astype(str)
    return df_result