import pandas as pd
import pandas_ta as ta

def calculate_indicators(df):
    """Calculates multiple technical indicators."""
    # Ensure dataframe is not too small
    if len(df) < 20:
        return df

    # RSI
    df.ta.rsi(length=14, append=True)

    # Bollinger Bands
    df.ta.bbands(length=20, std=2, append=True)

    # EMA
    df.ta.ema(length=9, append=True)
    df.ta.ema(length=21, append=True)

    # MACD
    df.ta.macd(append=True)

    return df

def detect_support_resistance(df, window=20):
    """Simple support and resistance detection based on local mins and maxs."""
    if len(df) < window:
        return [], []

    supports = []
    resistances = []

    for i in range(window, len(df) - window):
        # Support: low is less than all lows in window
        if df['low'].iloc[i] == df['low'].iloc[i-window:i+window].min():
            supports.append(df['low'].iloc[i])
        # Resistance: high is greater than all highs in window
        if df['high'].iloc[i] == df['high'].iloc[i-window:i+window].max():
            resistances.append(df['high'].iloc[i])

    # Remove duplicates/close values (higher precision for Forex)
    supports = sorted(list(set([round(s, 5) for s in supports])))
    resistances = sorted(list(set([round(r, 5) for r in resistances])))

    return supports[-3:], resistances[-3:] # Return top 3 most recent/relevant

def get_binary_signal(df):
    """Generate a simple Binary Option signal based on indicators."""
    if df.empty:
        return "NEUTRAL"

    latest = df.iloc[-1]

    # Simple strategy: RSI + BBands
    rsi = latest.get('RSI_14')
    bb_lower = latest.get('BBL_20_2.0')
    bb_upper = latest.get('BBU_20_2.0')
    close = latest['close']

    if rsi is not None and bb_lower is not None and close < bb_lower and rsi < 30:
        return "CALL (BUY) - Oversold"
    elif rsi is not None and bb_upper is not None and close > bb_upper and rsi > 70:
        return "PUT (SELL) - Overbought"
    else:
        return "NEUTRAL"
