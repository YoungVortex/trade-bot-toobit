import json
import pandas as pd
import numpy as np
import mplfinance as mpf

def compute_supertrend(df, period=10, multiplier=3):
    """
    Compute SuperTrend indicator for a given DataFrame with columns:
    'High', 'Low', 'Close'.
    Returns a pandas Series containing the SuperTrend line values.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']

    # True Range
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    # Basic upper and lower bands
    hl2 = (high + low) / 2
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr

    # Initialize trend and SuperTrend series
    st = pd.Series(index=df.index, dtype=float)
    trend = pd.Series(index=df.index, dtype=int)  # 1 = uptrend, -1 = downtrend

    for i in range(1, len(df)):
        if close.iloc[i] > upper.iloc[i-1]:
            trend.iloc[i] = 1
        elif close.iloc[i] < lower.iloc[i-1]:
            trend.iloc[i] = -1
        else:
            trend.iloc[i] = trend.iloc[i-1]
            # Adjust bands when trend continues
            if trend.iloc[i] == 1 and lower.iloc[i] < lower.iloc[i-1]:
                lower.iloc[i] = lower.iloc[i-1]
            if trend.iloc[i] == -1 and upper.iloc[i] > upper.iloc[i-1]:
                upper.iloc[i] = upper.iloc[i-1]

        # SuperTrend line is the band on the opposite side of the trend
        st.iloc[i] = lower.iloc[i] if trend.iloc[i] == 1 else upper.iloc[i]

    st.iloc[0] = np.nan   # no value for the first bar
    return st

def export_candles(json_file, output_file="chart.png"):
    # Read JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        raise ValueError("JSON file is empty.")

    # Create DataFrame
    df = pd.DataFrame(data)

    # Rename columns
    df.rename(columns={
        "open_time": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    }, inplace=True)

    # Convert timestamp
    df["Date"] = pd.to_datetime(df["Date"], unit="ms")

    # Convert numeric columns
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col])

    # Keep only required columns
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

    # Set datetime index
    df.set_index("Date", inplace=True)

    # --------------------------------------------------------------------
    # Compute three SuperTrend indicators (all length 10, multipliers 1,2,3)
    # --------------------------------------------------------------------
    supertrends = [
        {"period": 10, "multiplier": 1, "color": "cyan", "label": "ST1"},
        {"period": 10, "multiplier": 2, "color": "magenta", "label": "ST2"},
        {"period": 10, "multiplier": 3, "color": "yellow", "label": "ST3"}
    ]

    addplots = []
    for st in supertrends:
        st_series = compute_supertrend(df, period=st["period"], multiplier=st["multiplier"])
        addplot = mpf.make_addplot(
            st_series,
            color=st["color"],
            width=1.0,
            linestyle='-',
            label=st["label"],
            secondary_y=False   # plot on main price axis
        )
        addplots.append(addplot)

    # ---------------- Market Colors ---------------- #
    mc = mpf.make_marketcolors(
        up="white",
        down="#808080",
        edge={
            "up": "white",
            "down": "#808080",
        },
        wick={
            "up": "white",
            "down": "#808080",
        },
        volume={
            "up": "white",
            "down": "#808080",
        },
    )

    style = mpf.make_mpf_style(
        base_mpf_style="nightclouds",
        marketcolors=mc,
        facecolor="#131722",
        figcolor="#131722",
        gridstyle="-",
        gridcolor="#2A2E39",
        y_on_right=True,
        rc={
            "axes.labelcolor": "white",
            "axes.edgecolor": "#555555",
            "xtick.color": "white",
            "ytick.color": "white",
            "figure.facecolor": "#131722",
            "savefig.facecolor": "#131722",
        },
    )

    # Plot the chart with all SuperTrends
    mpf.plot(
        df,
        type="candle",
        style=style,
        volume=True,
        addplot=addplots,             # <-- overlay the three SuperTrend lines
        figsize=(16, 9),
        tight_layout=True,
        xrotation=0,
        savefig=dict(
            fname=output_file,
            dpi=300,
            bbox_inches="tight",
        ),
    )

    print(f"Saved: {output_file}")

if __name__ == "__main__":
    export_candles("candles.json")