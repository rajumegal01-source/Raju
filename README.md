# Binary Option AI Trading Bot

A sophisticated Telegram bot providing real-time technical analysis and signals for Binary Options trading (Forex, Crypto, Gold).

## Features

- **Signal Generation**: Get high-precision CALL/PUT signals for multiple timeframes (1m, 2m, 3m, 5m).
- **Technical Indicators**: Uses RSI, Bollinger Bands, EMA, and MACD.
- **Support & Resistance**: Automatic detection of key market levels.
- **AI Analysis**: DeepSeek AI-powered market sentiment and detailed analysis.
- **Multi-Source Data**: Supports Twelve Data, Alpha Vantage, and Yahoo Finance.

## Commands

- `/start`: Interactive help and command list.
- `/price <ticker>`: Real-time price (e.g., `/price EUR/USD`).
- `/signal <ticker> <timeframe>`: Binary Option signal (e.g., `/signal BTC/USD 1min`).
- `/analyze <ticker>`: AI-powered market deep-dive.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Create a `.env` file from `.env.example` and add your API keys:
   - `TELEGRAM_BOT_TOKEN`: From BotFather.
   - `DEEPSEEK_API_KEY`: For AI Analysis.
   - `TWELVEDATA_API_KEY`: High-precision intraday data (Recommended).
   - `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`: Optional AI providers.

3. **Run**:
   ```bash
   python trading_bot.py
   ```

## Binary Options Strategy

The bot utilizes a combined strategy:
1. **Mean Reversion**: Uses Bollinger Bands to identify overextended price moves.
2. **Momentum**: RSI filter to confirm oversold/overbought conditions.
3. **Price Action**: Support and Resistance level validation.
