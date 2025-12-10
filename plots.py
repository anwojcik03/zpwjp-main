import plotly.graph_objects as go

def plot_price_interactive(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Close"],
        mode="lines",  # no markers
        name="Close price",
        hovertemplate=
            "<b>Date:</b> %{x}<br>" +
            "<b>Close:</b> %{y:.2f}<br>" +
            "<extra></extra>"
    ))

    fig.update_layout(
        title="Price over time",
        xaxis_title="Date",
        yaxis_title="Close",
        template="plotly_white",
        hovermode="x unified",
        height=420
    )

    return fig