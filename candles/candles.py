import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplfinance as mpf

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 600,
    "font.size": 10,
    "figure.facecolor": "#131722",
    "axes.facecolor": "#131722",
    "savefig.facecolor": "#131722",
})


def supertrend(df, length=10, multiplier=1.0):
    high = df["High"].values
    low = df["Low"].values
    close = df["Close"].values
    hl2 = (high + low) / 2.0

    tr = np.maximum(
        high - low,
        np.maximum(
            np.abs(high - np.roll(close, 1)),
            np.abs(low - np.roll(close, 1)),
        ),
    )
    tr[0] = high[0] - low[0]
    atr = pd.Series(tr).ewm(span=length, adjust=False).mean().values

    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr

    n = len(close)
    final_upper = np.copy(upper)
    final_lower = np.copy(lower)
    direction = np.ones(n, dtype=int)

    for i in range(1, n):
        if upper[i] < final_upper[i - 1] or close[i - 1] > final_upper[i - 1]:
            final_upper[i] = upper[i]
        else:
            final_upper[i] = final_upper[i - 1]
        if lower[i] > final_lower[i - 1] or close[i - 1] < final_lower[i - 1]:
            final_lower[i] = lower[i]
        else:
            final_lower[i] = final_lower[i - 1]
        if direction[i - 1] == 1 and close[i] < final_lower[i]:
            direction[i] = -1
        elif direction[i - 1] == -1 and close[i] > final_upper[i]:
            direction[i] = 1
        else:
            direction[i] = direction[i - 1]

    trend = np.where(direction == 1, final_lower, final_upper)
    return pd.Series(trend, index=df.index), pd.Series(direction, index=df.index)


def rsi(close, length=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(span=length, adjust=False).mean()
    avg_loss = loss.ewm(span=length, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def pivots(df, left=5, right=5):
    high = df["High"].values
    low = df["Low"].values
    n = len(high)
    pivot_high = np.full(n, np.nan)
    pivot_low = np.full(n, np.nan)
    for i in range(left, n - right):
        if high[i] == max(high[i - left : i + right + 1]):
            pivot_high[i] = high[i]
        if low[i] == min(low[i - left : i + right + 1]):
            pivot_low[i] = low[i]
    return pd.Series(pivot_high, index=df.index), pd.Series(pivot_low, index=df.index)


def smart_money(df, swing_length=5):
    o = df["Open"].values
    h = df["High"].values
    l = df["Low"].values
    c = df["Close"].values
    n = len(df)

    ph, pl = pivots(df, left=swing_length, right=swing_length)
    ph_vals, pl_vals = ph.values, pl.values

    bos_bull = np.zeros(n, dtype=bool)
    bos_bear = np.zeros(n, dtype=bool)
    choch_bull = np.zeros(n, dtype=bool)
    choch_bear = np.zeros(n, dtype=bool)
    last_swing_high = np.full(n, np.nan)
    last_swing_low = np.full(n, np.nan)
    swing_high_idx = np.full(n, -1, dtype=int)
    swing_low_idx = np.full(n, -1, dtype=int)
    trend = np.zeros(n, dtype=int)

    current_sh = current_sl = np.nan
    current_sh_idx = current_sl_idx = -1
    current_trend = 0

    for i in range(1, n):
        if not np.isnan(ph_vals[i]):
            current_sh, current_sh_idx = ph_vals[i], i
        if not np.isnan(pl_vals[i]):
            current_sl, current_sl_idx = pl_vals[i], i
        last_swing_high[i], last_swing_low[i] = current_sh, current_sl
        swing_high_idx[i], swing_low_idx[i] = current_sh_idx, current_sl_idx

        if not np.isnan(current_sh) and c[i] > current_sh and c[i - 1] <= current_sh:
            (choch_bull if current_trend == -1 else bos_bull)[i] = True
            current_trend = 1
        if not np.isnan(current_sl) and c[i] < current_sl and c[i - 1] >= current_sl:
            (choch_bear if current_trend == 1 else bos_bear)[i] = True
            current_trend = -1
        trend[i] = current_trend

    bull_ob = np.full(n, np.nan)
    bull_ob_low = np.full(n, np.nan)
    bear_ob = np.full(n, np.nan)
    bear_ob_low = np.full(n, np.nan)

    for i in range(1, n):
        if bos_bull[i] or choch_bull[i]:
            for j in range(i - 1, max(i - 6, -1), -1):
                if c[j] < o[j]:
                    bull_ob[i], bull_ob_low[i] = h[j], l[j]
                    break
        if bos_bear[i] or choch_bear[i]:
            for j in range(i - 1, max(i - 6, -1), -1):
                if c[j] > o[j]:
                    bear_ob[i], bear_ob_low[i] = h[j], l[j]
                    break

    fvg_bull_top = np.full(n, np.nan)
    fvg_bull_bot = np.full(n, np.nan)
    fvg_bear_top = np.full(n, np.nan)
    fvg_bear_bot = np.full(n, np.nan)

    for i in range(2, n):
        if l[i] > h[i - 2]:
            fvg_bull_top[i], fvg_bull_bot[i] = l[i], h[i - 2]
        if h[i] < l[i - 2]:
            fvg_bear_top[i], fvg_bear_bot[i] = l[i - 2], h[i]

    return {
        "bos_bull": bos_bull, "bos_bear": bos_bear,
        "choch_bull": choch_bull, "choch_bear": choch_bear,
        "bull_ob": bull_ob, "bull_ob_low": bull_ob_low,
        "bear_ob": bear_ob, "bear_ob_low": bear_ob_low,
        "fvg_bull_top": fvg_bull_top, "fvg_bull_bot": fvg_bull_bot,
        "fvg_bear_top": fvg_bear_top, "fvg_bear_bot": fvg_bear_bot,
        "last_swing_high": last_swing_high, "last_swing_low": last_swing_low,
        "swing_high_idx": swing_high_idx, "swing_low_idx": swing_low_idx,
    }


def export_candles(json_file, output_file="chart.png"):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        raise ValueError("JSON file is empty.")

    df = pd.DataFrame(data)
    df.rename(columns={
        "open_time": "Date", "open": "Open", "high": "High",
        "low": "Low", "close": "Close", "volume": "Volume",
    }, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], unit="ms")
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col])
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df.set_index("Date", inplace=True)

    # TradingView-style colors
    mc = mpf.make_marketcolors(
        up="#26a69a", down="#ef5350",
        edge={"up": "#26a69a", "down": "#ef5350"},
        wick={"up": "#26a69a", "down": "#ef5350"},
        volume={"up": "#26a69a", "down": "#ef5350"},
    )
    style = mpf.make_mpf_style(
        base_mpf_style="nightclouds", marketcolors=mc,
        facecolor="#131722", figcolor="#131722",
        gridstyle="-", gridcolor="#1e222d", y_on_right=True,
        rc={
            "axes.labelcolor": "#d1d4dc", "axes.edgecolor": "#1e222d",
            "xtick.color": "#d1d4dc", "ytick.color": "#d1d4dc",
            "figure.facecolor": "#131722", "savefig.facecolor": "#131722",
        },
    )

    # Indicators
    st1, dir1 = supertrend(df, 10, 1.0)
    st2, dir2 = supertrend(df, 10, 2.0)
    st3, dir3 = supertrend(df, 10, 3.0)
    rsi_val = rsi(df["Close"], 14)
    ph, pl = pivots(df, 5, 5)
    sm = smart_money(df, 5)

    price_min, price_max = df["Low"].min(), df["High"].max()
    rsi_scaled = (rsi_val / 100) * (price_max - price_min) + price_min
    ph_line, pl_line = ph.ffill(), pl.ffill()

    def split_seg(vals, dirs):
        n = len(vals)
        up_mask, dn_mask = dirs == 1, dirs == -1
        for i in range(1, n):
            if dirs[i] != dirs[i - 1]:
                (up_mask if dirs[i] == 1 else dn_mask)[i - 1] = True
        u, d = vals.copy().astype(float), vals.copy().astype(float)
        u[~up_mask] = np.nan
        d[~dn_mask] = np.nan
        return u, d

    s1u, s1d = [pd.Series(x, index=df.index) for x in split_seg(st1.values, dir1.values)]
    s2u, s2d = [pd.Series(x, index=df.index) for x in split_seg(st2.values, dir2.values)]
    s3u, s3d = [pd.Series(x, index=df.index) for x in split_seg(st3.values, dir3.values)]

    ap = [
        mpf.make_addplot(s1u, color="#26a69a", width=2),
        mpf.make_addplot(s1d, color="#ef5350", width=2),
        mpf.make_addplot(s2u, color="#26a69a", width=1.5, linestyle="--"),
        mpf.make_addplot(s2d, color="#ef5350", width=1.5, linestyle="--"),
        mpf.make_addplot(s3u, color="#26a69a", width=1, linestyle=":"),
        mpf.make_addplot(s3d, color="#ef5350", width=1, linestyle=":"),
        mpf.make_addplot(rsi_scaled, color="#7b1fa2", width=1.5),
        mpf.make_addplot(ph_line, color="#2962ff", width=2, linestyle="--"),
        mpf.make_addplot(pl_line, color="#ff6d00", width=2, linestyle="--"),
        mpf.make_addplot(ph, type="scatter", marker="v", markersize=60, color="#ef5350"),
        mpf.make_addplot(pl, type="scatter", marker="^", markersize=60, color="#26a69a"),
    ]

    d1, d2, d3 = dir1.iloc[-1], dir2.iloc[-1], dir3.iloc[-1]

    fig, axes = mpf.plot(
        df, type="candle", style=style, volume=True, addplot=ap,
        figsize=(24, 16), panel_ratios=(5, 1),
        tight_layout=True, xrotation=0, returnfig=True,
    )
    axes[0].set_facecolor("#131722")
    axes[1].set_facecolor("#131722")
    ax = axes[0]

    # Structure lines
    for i in range(len(df)):
        if sm["bos_bull"][i] or sm["choch_bull"][i]:
            si = sm["swing_low_idx"][i]
            lv = sm["last_swing_low"][i]
            if si >= 0:
                c = "#26a69a" if sm["bos_bull"][i] else "#00e676"
                ax.plot([si, i], [lv, lv], color=c, linewidth=1.5, alpha=0.8)
        if sm["bos_bear"][i] or sm["choch_bear"][i]:
            si = sm["swing_high_idx"][i]
            lv = sm["last_swing_high"][i]
            if si >= 0:
                c = "#ef5350" if sm["bos_bear"][i] else "#ff9100"
                ax.plot([si, i], [lv, lv], color=c, linewidth=1.5, alpha=0.8)

    # BOS/CHoCH labels
    for i in range(len(df)):
        if sm["bos_bull"][i]:
            ax.text(i, df["Low"].iloc[i] * 0.997, "BOS", fontsize=7, color="white",
                    ha="center", va="top", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#2157f3", edgecolor="none", alpha=0.95))
        if sm["bos_bear"][i]:
            ax.text(i, df["High"].iloc[i] * 1.003, "BOS", fontsize=7, color="white",
                    ha="center", va="bottom", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#F23645", edgecolor="none", alpha=0.95))
        if sm["choch_bull"][i]:
            ax.text(i, df["Low"].iloc[i] * 0.997, "CHoCH", fontsize=7, color="white",
                    ha="center", va="top", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#00e676", edgecolor="none", alpha=0.95))
        if sm["choch_bear"][i]:
            ax.text(i, df["High"].iloc[i] * 1.003, "CHoCH", fontsize=7, color="white",
                    ha="center", va="bottom", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#ff9100", edgecolor="none", alpha=0.95))

    h_vals, l_vals = df["High"].values, df["Low"].values

    # Order Blocks (until mitigated)
    for i in range(len(df)):
        if not np.isnan(sm["bull_ob"][i]):
            top, bot = sm["bull_ob"][i], sm["bull_ob_low"][i]
            end = next((j for j in range(i + 1, len(df)) if l_vals[j] < bot), len(df))
            ax.add_patch(plt.Rectangle((i - 0.5, bot), end - i, top - bot,
                         facecolor="#2962ff", alpha=0.15, edgecolor="#2962ff", linewidth=0.5, linestyle="--"))
        if not np.isnan(sm["bear_ob"][i]):
            top, bot = sm["bear_ob"][i], sm["bear_ob_low"][i]
            end = next((j for j in range(i + 1, len(df)) if h_vals[j] > top), len(df))
            ax.add_patch(plt.Rectangle((i - 0.5, bot), end - i, top - bot,
                         facecolor="#ef5350", alpha=0.15, edgecolor="#ef5350", linewidth=0.5, linestyle="--"))

    # FVG (until filled)
    for i in range(len(df)):
        if not np.isnan(sm["fvg_bull_top"][i]):
            top, bot = sm["fvg_bull_top"][i], sm["fvg_bull_bot"][i]
            end = next((j for j in range(i + 1, len(df)) if l_vals[j] <= bot), len(df))
            ax.add_patch(plt.Rectangle((i - 0.5, bot), end - i, top - bot,
                         facecolor="#26a69a", alpha=0.12, edgecolor="#26a69a", linewidth=0.5, linestyle="--"))
        if not np.isnan(sm["fvg_bear_top"][i]):
            top, bot = sm["fvg_bear_top"][i], sm["fvg_bear_bot"][i]
            end = next((j for j in range(i + 1, len(df)) if h_vals[j] >= top), len(df))
            ax.add_patch(plt.Rectangle((i - 0.5, bot), end - i, top - bot,
                         facecolor="#ef5350", alpha=0.12, edgecolor="#ef5350", linewidth=0.5, linestyle="--"))

    # Title
    fig.suptitle("Smart Money Concepts  •  Triple SuperTrend  •  RSI",
                 fontsize=15, fontweight="bold", color="#d1d4dc", y=0.98)

    # SuperTrend table (top-left)
    tbl = ""
    for lbl, d in [("ST 1", d1), ("ST 2", d2), ("ST 3", d3)]:
        arr = "▲" if d == 1 else "▼"
        clr = "#26a69a" if d == 1 else "#ef5350"
        tbl += f"\033[{clr}m{lbl} : {arr} {'Up' if d == 1 else 'Down'}\033[0m\n"
    # plain text version
    tbl = ""
    for lbl, d in [("ST 1", d1), ("ST 2", d2), ("ST 3", d3)]:
        arr = "▲" if d == 1 else "▼"
        tbl += f"{lbl} : {arr} {'Up' if d == 1 else 'Down'}\n"
    ax.text(0.01, 0.98, tbl.strip(), transform=ax.transAxes, fontsize=10, fontfamily="monospace",
            fontweight="bold", va="top", ha="left", color="white",
            bbox=dict(boxstyle="round,pad=0.5", fc="#1a1a2e", ec="#333333", alpha=0.95))

    # Legend (bottom-right)
    legend = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  INDICATORS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        " ───  SuperTrend (Green Up / Red Down)\n"
        " ───  RSI 14 (Purple)\n"
        " - - -  Pivot High (Blue) / Low (Orange)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  SMART MONEY\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        " [BOS]    Break of Structure\n"
        " [CHoCH]  Change of Character\n"
        " ▓▓▓      Bullish Order Block (Blue)\n"
        " ▓▓▓      Bearish Order Block (Red)\n"
        " ▓▓▓      Bullish FVG (Teal)\n"
        " ▓▓▓      Bearish FVG (Red)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    ax.text(0.99, 0.01, legend, transform=ax.transAxes, fontsize=8, fontfamily="monospace",
            va="bottom", ha="right", color="#d1d4dc", linespacing=1.3,
            bbox=dict(boxstyle="round,pad=0.6", fc="#1a1a2e", ec="#333333", alpha=0.95))

    fig.savefig(output_file, dpi=600, bbox_inches="tight", facecolor="#131722",
                pad_inches=0.3, pil_kwargs={"antialias": "best"})
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    export_candles("candles.json")
