import json
import pandas as pd
import mplfinance as mpf


def export_candles(json_file, output_file="chart.png"):
    # Read JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        raise ValueError("JSON file is empty.")

    # Create DataFrame
    df = pd.DataFrame(data)

    # Rename columns
    df = df.rename(columns={
        "open_time": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    })

    # Convert timestamp
    df["Date"] = pd.to_datetime(df["Date"], unit="ms")

    # Convert numeric columns
    numeric_columns = ["Open", "High", "Low", "Close", "Volume"]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="raise")

    # Keep only required columns
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

    # Set datetime index
    df.set_index("Date", inplace=True)

    # Sort by time
    df.sort_index(inplace=True)

    # ---------------- DEBUG ----------------
    print("\nColumns:")
    print(df.columns)

    print("\nData Types:")
    print(df.dtypes)

    print("\nFirst Rows:")
    print(df.head())
    # ---------------------------------------

    # TradingView-like colors
    mc = mpf.make_marketcolors(
        up="#26a69a",
        down="#ef5350",
        edge="inherit",
        wick="inherit",
        volume="inherit",
    )

    style = mpf.make_mpf_style(
        base_mpf_style="nightclouds",
        marketcolors=mc,
        facecolor="#131722",
        figcolor="#131722",
        gridcolor="#2A2E39",
        gridstyle="-",
        rc={
            "axes.labelcolor": "white",
            "xtick.color": "white",
            "ytick.color": "white",
        },
    )

    mpf.plot(
        df,
        type="candle",
        style=style,
        volume=True,
        figsize=(16, 9),
        tight_layout=True,
        savefig=dict(
            fname=output_file,
            dpi=300,
            bbox_inches="tight",
        ),
    )

    print(f"\nChart saved to: {output_file}")


if __name__ == "__main__":
    export_candles("candles.json")