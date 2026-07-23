# Toobit Engine — Smart Money Chart Generator

Professional trading chart generator with **Smart Money Concepts**, **Triple SuperTrend**, **RSI**, and **Pivot Points** — exported as high-resolution PNG images.

## Features

### Triple SuperTrend
- **ST 1**: Length 10, Multiplier 1.0 (Solid line)
- **ST 2**: Length 10, Multiplier 2.0 (Dashed line)
- **ST 3**: Length 10, Multiplier 3.0 (Dotted line)
- Green = Bullish trend, Red = Bearish trend

### RSI (Relative Strength Index)
- 14-period RSI in separate panel
- Overbought (70) / Oversold (30) reference lines
- Real-time status: OVERBOUGHT / OVERSOLD / NEUTRAL

### Pivot Points
- Pivot High (Orange ▼ markers + dashed line)
- Pivot Low (Green ▲ markers + dashed line)
- 5-bar lookback on each side

### Smart Money Concepts
- **BOS** (Break of Structure) — Blue/Red labels
- **CHoCH** (Change of Character) — Teal/Orange labels
- **Order Blocks** — Bullish (Blue) / Bearish (Red) shaded zones
- **Fair Value Gaps** — Bullish (Cyan) / Bearish (Red) shaded zones
- Structure lines connecting swing points to breakouts

## Chart Layout

| Panel | Content |
|-------|---------|
| Panel 0 | Candles + SuperTrend + Pivots + Smart Money |
| Panel 1 | Volume |
| Panel 2 | RSI (14) |

## Installation

```bash
pip install numpy pandas matplotlib mplfinance
```

## Usage

```bash
cd candles
python candles.py
```

### Input
- `candles.json` — OHLCV data in JSON format

### Output
- `chart.png` — High-resolution chart (600 DPI)

### JSON Format

```json
[
  {
    "open_time": 1689000000000,
    "open": 64500.0,
    "high": 65200.0,
    "low": 64100.0,
    "close": 64800.0,
    "volume": 1234.5
  }
]
```

## Customization

Edit `candles.py` to change indicator parameters:

```python
# SuperTrend settings
st1, d1 = supertrend(df, 10, 1.0)  # length, multiplier
st2, d2 = supertrend(df, 10, 2.0)
st3, d3 = supertrend(df, 10, 3.0)

# RSI period
rv = rsi(df["Close"], 14)

# Pivot lookback
ph, pl = pivots(df, 5, 5)  # left, right bars

# Smart Money swing length
sm = smart_money(df, 5)
```

## Theme

Dark theme inspired by TradingView:
- Background: `#0d1117`
- Bullish: `#3fb950`
- Bearish: `#f85149`
- Grid: `#21262d`

## License

Created by Toobit Engine
