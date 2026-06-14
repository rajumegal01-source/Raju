# Binary Option AI Trading Bot

A high-performance Telegram bot for Binary Options (Forex, Crypto, Gold) with multi-AI analysis.

## Features

- **Multi-AI Analysis**: Choose between DeepSeek, Gemini, Groq, and OpenRouter for market insights.
- **Precision Signals**: CALL/PUT signals for 1m, 2m, 3m, and 5m timeframes.
- **Advanced Indicators**: RSI, Bollinger Bands, and EMA crossover strategies.
- **Market Levels**: Automatic Support and Resistance detection.
- **Multi-Source Data**: Twelve Data (Precision Intraday) and Yahoo Finance.

## Commands

- `/start`: Interactive help and command list.
- `/price <ticker>`: Real-time price (e.g., `/price BTC-USD`).
- `/signal <ticker> <timeframe>`: Binary Option signal (e.g., `/signal EUR/USD 1min`).
- `/analyze <ticker> <provider>`: AI Analysis using `deepseek`, `gemini`, `groq`, or `openrouter`.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Copy `.env.example` to `.env` and add your keys.

3. **Run**:
   ```bash
   python trading_bot.py
   ```
