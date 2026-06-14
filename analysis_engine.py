import pandas as pd
import pandas_ta as ta

def calculate_indicators(df):
    """Calculates multiple technical indicators."""
    # Ensure dataframe is not too small
    if len(df) < 30:
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
    if df.empty or 'RSI_14' not in df.columns:
        return "NEUTRAL"

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    rsi = latest['RSI_14']
    bb_lower = latest['BBL_20_2.0']
    bb_upper = latest['BBU_20_2.0']
    ema9 = latest['EMA_9']
    ema21 = latest['EMA_21']
    close = latest['close']

    # Buy Signal: RSI Oversold + BB Lower Break + EMA Bullish Cross or Close > EMA9
    if rsi < 35 and close < bb_lower and close > ema9:
        return "CALL (BUY) - Oversold Recovery"

    # Sell Signal: RSI Overbought + BB Upper Break + Close < EMA9
    elif rsi > 65 and close > bb_upper and close < ema9:
        return "PUT (SELL) - Overbought Reversal"

    # Trend Following: EMA Cross
    elif ema9 > ema21 and prev['EMA_9'] <= prev['EMA_21']:
        return "CALL (BUY) - Bullish EMA Cross"
    elif ema9 < ema21 and prev['EMA_9'] >= prev['EMA_21']:
        return "PUT (SELL) - Bearish EMA Cross"

    else:
        return "NEUTRAL"
